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
def read_reseller(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.MasterUser).filter(models.MasterUser.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Reseller not found")
    return map_db_to_schema(user)


# --- Business User Routes ---

def map_db_business_to_schema(db_user: models.BusinessUser):
    return {
        "user_id": db_user.user_id,
        "parent_reseller_id": db_user.parent_reseller_id,
        "role": db_user.role,
        "status": db_user.status,
        "whatsapp_mode": db_user.whatsapp_mode,
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
        "wallet": {
            "credits_allocated": db_user.credits_allocated,
            "credits_used": db_user.credits_used,
            "credits_remaining": db_user.credits_remaining,
        }
    }

@app.post("/business-users", response_model=schemas.BusinessUserRead)
def create_business_user(user: schemas.BusinessUserCreate, db: Session = Depends(get_db)):
    # Validate Parent Reseller
    reseller = db.query(models.MasterUser).filter(models.MasterUser.user_id == user.parent_reseller_id).first()
    if not reseller:
        raise HTTPException(status_code=404, detail="Parent Reseller not found")

    # Check duplications
    if db.query(models.BusinessUser).filter(models.BusinessUser.email == user.profile.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.BusinessUser).filter(models.BusinessUser.username == user.profile.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pwd = "hashed_" + user.profile.password

    db_user = models.BusinessUser(
        parent_reseller_id=user.parent_reseller_id,
        role=user.role,
        status=user.status,
        whatsapp_mode=user.whatsapp_mode,
        # Profile
        name=user.profile.name,
        username=user.profile.username,
        email=user.profile.email,
        phone=user.profile.phone,
        password_hash=hashed_pwd,
        # Business
        business_name=user.business.business_name,
        business_description=user.business.business_description,
        erp_system=user.business.erp_system,
        gstin=user.business.gstin,
        # Address
        full_address=user.address.full_address,
        pincode=user.address.pincode,
        country=user.address.country,
        # Wallet
        credits_allocated=user.wallet.credits_allocated if user.wallet else 0.0,
        credits_used=user.wallet.credits_used if user.wallet else 0.0,
        credits_remaining=user.wallet.credits_remaining if user.wallet else 0.0,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return map_db_business_to_schema(db_user)

@app.get("/business-users", response_model=List[schemas.BusinessUserRead])
def read_business_users(reseller_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.BusinessUser)
    if reseller_id:
        query = query.filter(models.BusinessUser.parent_reseller_id == reseller_id)
    
    users = query.offset(skip).limit(limit).all()
    return [map_db_business_to_schema(user) for user in users]

@app.get("/business-users/{user_id}", response_model=schemas.BusinessUserRead)
def read_business_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.BusinessUser).filter(models.BusinessUser.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Business User not found")
    return map_db_business_to_schema(user)

# --- Credit Distribution Routes ---

@app.post("/credits/distribute", response_model=schemas.CreditTransactionRead)
def distribute_credits(transaction: schemas.CreditDistributionCreate, db: Session = Depends(get_db)):
    # 1. Get Reseller
    reseller = db.query(models.MasterUser).filter(models.MasterUser.user_id == transaction.from_reseller_id).first()
    if not reseller:
        raise HTTPException(status_code=404, detail="Reseller not found")
    
    # 2. Get Business User
    business_user = db.query(models.BusinessUser).filter(models.BusinessUser.user_id == transaction.to_business_user_id).first()
    if not business_user:
        raise HTTPException(status_code=404, detail="Business User not found")

    # 3. Validation: Verify ownership (optional but recommended)
    if business_user.parent_reseller_id != reseller.user_id:
         raise HTTPException(status_code=403, detail="Reseller does not own this Business User")

    # 4. Check Balance
    if reseller.available_credits < transaction.credits:
        raise HTTPException(status_code=400, detail="Insufficient credits in Reseller wallet")

    # 5. Perform Transaction (Atomic)
    try:
        # Reseller: Deduct available, Add used
        reseller.available_credits -= transaction.credits
        reseller.used_credits += transaction.credits

        # Business User: Add allocated, Add remaining
        business_user.credits_allocated += transaction.credits
        business_user.credits_remaining += transaction.credits
        
        # Record Transaction
        db_transaction = models.CreditTransaction(
            from_reseller_id=transaction.from_reseller_id,
            to_business_user_id=transaction.to_business_user_id,
            credits_shared=transaction.credits
        )
        db.add(db_transaction)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/credits/history", response_model=List[schemas.CreditTransactionRead])
def read_credit_history(reseller_id: str = None, business_user_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.CreditTransaction)
    
    if reseller_id:
        query = query.filter(models.CreditTransaction.from_reseller_id == reseller_id)
    if business_user_id:
        query = query.filter(models.CreditTransaction.to_business_user_id == business_user_id)
        
    return query.order_by(models.CreditTransaction.shared_at.desc()).offset(skip).limit(limit).all()
