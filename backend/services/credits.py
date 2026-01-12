from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import schemas
from ..crud import credits as crud_credits

class CreditService:
    def __init__(self, db: Session):
        self.db = db

    def distribute(self, data: schemas.CreditDistributionCreate):
        # 1. Fetch Actors
        reseller = crud_credits.get_reseller(self.db, data.from_reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        business_user = crud_credits.get_business_user(self.db, data.to_business_user_id)
        if not business_user:
            raise HTTPException(status_code=404, detail="Business User not found")

        # 2. Validation
        if business_user.parent_reseller_id != reseller.user_id:
            raise HTTPException(status_code=403, detail="Reseller does not own this Business User")

        if reseller.available_credits < data.credits:
            raise HTTPException(status_code=400, detail="Insufficient credits")

        # 3. Execution (Atomic)
        try:
            reseller.available_credits -= data.credits
            reseller.used_credits += data.credits
            
            business_user.credits_allocated += data.credits
            business_user.credits_remaining += data.credits
            
            # Create Transaction Record
            db_tx = crud_credits.create_transaction(self.db, data)
            
            self.db.commit()
            self.db.refresh(db_tx)
            return db_tx
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_history(self, reseller_id: str = None, business_user_id: str = None, skip: int = 0, limit: int = 100):
        return crud_credits.get_history(self.db, reseller_id, business_user_id, skip, limit)
