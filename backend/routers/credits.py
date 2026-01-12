from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, database
from ..services.credits import CreditService

router = APIRouter(
    prefix="/credits",
    tags=["Credits"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/distribute", response_model=schemas.CreditTransactionRead)
def distribute_credits(transaction: schemas.CreditDistributionCreate, db: Session = Depends(get_db)):
    service = CreditService(db)
    return service.distribute(transaction)

@router.get("/history", response_model=List[schemas.CreditTransactionRead])
def read_credit_history(
    reseller_id: str = None, 
    business_user_id: str = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    service = CreditService(db)
    return service.get_history(reseller_id, business_user_id, skip, limit)
