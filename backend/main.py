from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import models, schemas, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def map_db_to_schema(db_user: models.MasterUser):
    return {
        "user_id": db_user.user_id,
        "role": db_user.role,
        "status": db_user.status,
        "created_at": db_user.created_at,
        "profile": {
            "name": db_user.name,
            "username": db_user.username,
            "email": db_user.email,
            "phone": db_user.phone,
        },
        "business": {
            "business_name": db_user.business_name,
            "business_description": db_user.business_description,
            "erp_system": db_user.erp_system,
            "gstin": db_user.gstin,
        },
        "address": {
            "full_address": db_user.full_address,
            "pincode": db_user.pincode,
            "country": db_user.country,
        },
        "bank": {
            "bank_name": db_user.bank_name,
        },
        "wallet": {
            "total_credits": db_user.total_credits,
            "available_credits": db_user.available_credits,
            "used_credits": db_user.used_credits,
        }
    }

@app.post("/resellers", response_model=schemas.ResellerRead)
def create_reseller(reseller: schemas.ResellerCreate, db: Session = Depends(get_db)):
    # Check existing
    if db.query(models.MasterUser).filter(models.MasterUser.email == reseller.profile.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.MasterUser).filter(models.MasterUser.username == reseller.profile.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Simple mock hash
    hashed_pwd = "hashed_" + reseller.profile.password

    db_user = models.MasterUser(
        role=reseller.role,
        status=reseller.status,
        # Profile
        name=reseller.profile.name,
        username=reseller.profile.username,
        email=reseller.profile.email,
        phone=reseller.profile.phone,
        password_hash=hashed_pwd,
        # Business
        business_name=reseller.business.business_name,
        business_description=reseller.business.business_description,
        erp_system=reseller.business.erp_system,
        gstin=reseller.business.gstin,
        # Address
        full_address=reseller.address.full_address,
        pincode=reseller.address.pincode,
        country=reseller.address.country,
        # Bank
        bank_name=reseller.bank.bank_name,
        # Wallet
        total_credits=reseller.wallet.total_credits if reseller.wallet else 0.0,
        available_credits=reseller.wallet.available_credits if reseller.wallet else 0.0,
        used_credits=reseller.wallet.used_credits if reseller.wallet else 0.0,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return map_db_to_schema(db_user)

@app.get("/resellers", response_model=List[schemas.ResellerRead])
def read_resellers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.MasterUser).offset(skip).limit(limit).all()
    return [map_db_to_schema(user) for user in users]

@app.get("/resellers/{user_id}", response_model=schemas.ResellerRead)
def read_reseller(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.MasterUser).filter(models.MasterUser.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Reseller not found")
    return map_db_to_schema(user)
