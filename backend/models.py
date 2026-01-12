import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Enum, Text
# from sqlalchemy.dialects.postgresql import UUID # Removed for SQLite compatibility
from database import Base

class MasterUser(Base):
    __tablename__ = "master_users"

    # Changed to String for SQLite compatibility. 
    # Pydantic will still handle this as a UUID object if formatted correctly.
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    role = Column(String, default="reseller") # reseller | admin
    status = Column(String, default="active")
    
    # Profile
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    password_hash = Column(String, nullable=False)
    
    # Business
    business_name = Column(String)
    business_description = Column(Text)
    erp_system = Column(String)
    gstin = Column(String)
    
    # Address
    full_address = Column(Text)
    pincode = Column(String)
    country = Column(String)
    
    # Bank
    bank_name = Column(String)
    
    # Wallet
    total_credits = Column(Float, default=0.0)
    available_credits = Column(Float, default=0.0)
    used_credits = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
