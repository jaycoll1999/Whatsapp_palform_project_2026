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

class BusinessUser(Base):
    __tablename__ = "business_users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_reseller_id = Column(String, nullable=False) # Foreign Key logic handling manually for SQLite simplicity or can use ForeignKey
    role = Column(String, default="business_owner")
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

    # Wallet
    credits_allocated = Column(Float, default=0.0)
    credits_used = Column(Float, default=0.0)
    credits_remaining = Column(Float, default=0.0)

    # WhatsApp Config
    whatsapp_mode = Column(String, default="official") # official | unofficial

    created_at = Column(DateTime, default=datetime.utcnow)

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    distribution_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_reseller_id = Column(String, nullable=False)
    to_business_user_id = Column(String, nullable=False)
    credits_shared = Column(Float, nullable=False)
    shared_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    channel = Column(String, default="whatsapp")
    mode = Column(String) # official | unofficial
    sender_number = Column(String)
    receiver_number = Column(String)
    message_type = Column(String, default="text") # text | template
    template_name = Column(String, nullable=True)
    message_body = Column(Text)
    status = Column(String, default="sent")
    credits_used = Column(Float, default=0.0)
    sent_at = Column(DateTime, default=datetime.utcnow)

class LinkedDevice(Base):
    __tablename__ = "linked_devices"

    device_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    device_name = Column(String)
    device_type = Column(String, default="whatsapp_web") # whatsapp_web | meta_api
    session_status = Column(String, default="disconnected") # connected | disconnected | scanning
    qr_last_generated = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    last_active = Column(DateTime, default=datetime.utcnow)
