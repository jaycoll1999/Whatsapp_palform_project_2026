from pydantic import BaseModel, Field
# from pydantic import EmailStr # Commented out to reduce dependency issues if email-validator is missing
from uuid import UUID
from datetime import datetime
from typing import Optional

class ProfileBase(BaseModel):
    name: str
    username: str
    email: str # Changed from EmailStr to str
    phone: Optional[str] = None

class ProfileCreate(ProfileBase):
    password: str

class ProfileRead(ProfileBase):
    pass

class BusinessBase(BaseModel):
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    erp_system: Optional[str] = None
    gstin: Optional[str] = None

class AddressBase(BaseModel):
    full_address: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None

class BankBase(BaseModel):
    bank_name: Optional[str] = None

class WalletBase(BaseModel):
    total_credits: float = 0.0
    available_credits: float = 0.0
    used_credits: float = 0.0

# Create Schema
class ResellerCreate(BaseModel):
    role: str = "reseller"
    status: str = "active"
    profile: ProfileCreate
    business: BusinessBase
    address: AddressBase
    bank: BankBase
    wallet: Optional[WalletBase] = None

# Read Schema
class ResellerRead(BaseModel):
    # user_id: UUID # Changed to str to match models.py SQLite compatibility
    user_id: str
    role: str
    status: str
    profile: ProfileRead
    business: BusinessBase
    address: AddressBase
    bank: BankBase
    wallet: WalletBase
    created_at: datetime

    class Config:
        from_attributes = True

class BusinessWalletBase(BaseModel):
    credits_allocated: float = 0.0
    credits_used: float = 0.0
    credits_remaining: float = 0.0

class BusinessUserCreate(BaseModel):
    role: str = "business_owner"
    status: str = "active"
    parent_reseller_id: str
    whatsapp_mode: str = "official"
    profile: ProfileCreate
    business: BusinessBase
    address: AddressBase
    wallet: Optional[BusinessWalletBase] = None

class BusinessUserRead(BaseModel):
    user_id: str
    parent_reseller_id: str
    role: str
    status: str
    whatsapp_mode: str
    profile: ProfileRead
    business: BusinessBase
    address: AddressBase
    wallet: BusinessWalletBase
    created_at: datetime

    class Config:
        from_attributes = True

class CreditDistributionCreate(BaseModel):
    from_reseller_id: str
    to_business_user_id: str
    credits: float

class CreditTransactionRead(BaseModel):
    distribution_id: str
    from_reseller_id: str
    to_business_user_id: str
    credits_shared: float
    shared_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    user_id: str
    mode: str = "official"
    sender_number: str
    receiver_number: str
    message_type: str = "text"
    template_name: Optional[str] = None
    message_body: str

class MessageRead(BaseModel):
    message_id: str
    user_id: str
    mode: str
    sender_number: str
    receiver_number: str
    message_type: str
    template_name: Optional[str] = None
    message_body: str
    status: str
    credits_used: float
    sent_at: datetime

    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    user_id: str
    device_name: str
    device_type: str = "whatsapp_web"

class DeviceRead(BaseModel):
    device_id: str
    user_id: str
    device_name: str
    device_type: str
    session_status: str
    ip_address: Optional[str] = None
    last_active: datetime

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    device_id: str

class SessionRead(BaseModel):
    session_id: str
    device_id: str
    session_token: str
    is_valid: str
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True
