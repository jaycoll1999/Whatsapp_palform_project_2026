from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
# Assume these imports exist
# from . import models, schemas
# from .database import get_db

"""
REFERENCE ARCHITECTURE: "Service Layer Pattern"
===============================================

Instead of putting all logic in main.py, we split it into:
1. ROUTER (Controller): Handles HTTP req/res, params, status codes.
2. SERVICE (Business Logic): Validations, calculations, decisions.
3. CRUD (Data Access): Only database reads/writes. No logic.

Example: Distributing Credits
"""

# --- 1. CRUD LAYER (crud.py) ---
# Handles raw DB operations. Doesn't know about HTTP.
class CreditCRUD:
    def get_reseller(self, db: Session, user_id: str):
        return db.query(models.MasterUser).filter(models.MasterUser.user_id == user_id).first()

    def get_business_user(self, db: Session, user_id: str):
        return db.query(models.BusinessUser).filter(models.BusinessUser.user_id == user_id).first()

    def create_transaction(self, db: Session, tx_data: schemas.CreditDistributionCreate):
        db_tx = models.CreditTransaction(**tx_data.dict())
        db.add(db_tx)
        # Note: No commit here if we want atomic transactions managed by Service
        return db_tx

# --- 2. SERVICE LAYER (services.py) ---
# Handles the rules. "You can't spend what you don't have."
class CreditService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = CreditCRUD()

    def distribute_credits(self, data: schemas.CreditDistributionCreate):
        # 1. Fetch Actors
        reseller = self.crud.get_reseller(self.db, data.from_reseller_id)
        if not reseller:
            raise ValueError("Reseller not found") # Service raises logical errors

        target = self.crud.get_business_user(self.db, data.to_business_user_id)
        if not target:
            raise ValueError("Business User not found")

        # 2. Business Logic Validation
        if reseller.available_credits < data.credits:
            raise ValueError(f"Insufficient funds. Has {reseller.available_credits}")

        # 3. Execution (Atomic)
        try:
            reseller.available_credits -= data.credits
            reseller.used_credits += data.credits
            
            target.credits_allocated += data.credits
            target.credits_remaining += data.credits

            self.crud.create_transaction(self.db, data)
            
            self.db.commit() # Service manages the transaction boundary
            return True
        except Exception as e:
            self.db.rollback()
            raise e

# --- 3. ROUTER LAYER (routers/credits.py) ---
# Handles the Web. Catches exceptions and returns correct HTTP codes.
router = APIRouter()

@router.post("/distribute")
def distribute_endpoint(data: schemas.CreditDistributionCreate, db: Session = Depends(get_db)):
    service = CreditService(db)
    try:
        service.distribute_credits(data)
        return {"status": "success", "message": "Credits distributed"}
    except ValueError as e:
        # Translate Logic Error -> HTTP 400/404
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Translate System Error -> HTTP 500
        raise HTTPException(status_code=500, detail="Internal Server Error")
