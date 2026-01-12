from sqlalchemy.orm import Session
from .. import models, schemas

def get_reseller(db: Session, user_id: str):
    return db.query(models.MasterUser).filter(models.MasterUser.user_id == user_id).first()

def get_business_user(db: Session, user_id: str):
    return db.query(models.BusinessUser).filter(models.BusinessUser.user_id == user_id).first()

def create_transaction(db: Session, tx_data: schemas.CreditDistributionCreate):
    db_tx = models.CreditTransaction(
        from_reseller_id=tx_data.from_reseller_id,
        to_business_user_id=tx_data.to_business_user_id,
        credits_shared=tx_data.credits
    )
    db.add(db_tx)
    return db_tx

def get_history(db: Session, reseller_id: str = None, business_user_id: str = None, skip: int = 0, limit: int = 100):
    query = db.query(models.CreditTransaction)
    if reseller_id:
        query = query.filter(models.CreditTransaction.from_reseller_id == reseller_id)
    if business_user_id:
        query = query.filter(models.CreditTransaction.to_business_user_id == business_user_id)
    return query.order_by(models.CreditTransaction.shared_at.desc()).offset(skip).limit(limit).all()
