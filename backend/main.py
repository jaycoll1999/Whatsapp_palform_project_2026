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

# --- Message Routes ---

def map_db_message_to_schema(db_msg: models.Message):
    return {
        "message_id": db_msg.message_id,
        "user_id": db_msg.user_id,
        "mode": db_msg.mode,
        "sender_number": db_msg.sender_number,
        "receiver_number": db_msg.receiver_number,
        "message_type": db_msg.message_type,
        "template_name": db_msg.template_name,
        "message_body": db_msg.message_body,
        "status": db_msg.status,
        "credits_used": db_msg.credits_used,
        "sent_at": db_msg.sent_at
    }

@app.post("/messages/send", response_model=schemas.MessageRead)
def send_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    # 1. Get User to check credits
    user = db.query(models.BusinessUser).filter(models.BusinessUser.user_id == msg.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Business User not found")

    # 2. Determine Cost (Mock Logic)
    # Official API typically costs money, Unofficial might be a flat fee or subscription.
    # We will assume: Official = 1 credit, Unofficial = 0.5 credits
    cost = 1.0 if msg.mode == "official" else 0.5
    
    if user.credits_remaining < cost:
         raise HTTPException(status_code=400, detail=f"Insufficient credits. Required: {cost}, Available: {user.credits_remaining}")

    # 3. Simulate Send (Mock)
    # In production, this would call WhatsApp API or Unofficial Gateway
    
    # 4. Deduct Credits Atomic
    try:
        user.credits_remaining -= cost
        user.credits_used += cost # Track total usage

        # 5. Record Message
        db_msg = models.Message(
            user_id=msg.user_id,
            mode=msg.mode,
            sender_number=msg.sender_number,
            receiver_number=msg.receiver_number,
            message_type=msg.message_type,
            template_name=msg.template_name,
            message_body=msg.message_body,
            status="sent",
            credits_used=cost
        )
        db.add(db_msg)
        
        # 6. Usage Log
        db_log = models.UsageLog(
            user_id=msg.user_id,
            message_id=db_msg.message_id,
            credits_deducted=cost,
            balance_after=user.credits_remaining
        )
        db.add(db_log)

        db.commit()
        db.refresh(db_msg)
        return map_db_message_to_schema(db_msg)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages", response_model=List[schemas.MessageRead])
def read_messages(user_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Message)
    if user_id:
        query = query.filter(models.Message.user_id == user_id)
    
    msgs = query.order_by(models.Message.sent_at.desc()).offset(skip).limit(limit).all()
    return [map_db_message_to_schema(m) for m in msgs]

# --- Linked Device Routes ---

def map_db_device_to_schema(db_dev: models.LinkedDevice):
    return {
        "device_id": db_dev.device_id,
        "user_id": db_dev.user_id,
        "device_name": db_dev.device_name,
        "device_type": db_dev.device_type,
        "session_status": db_dev.session_status,
        "ip_address": db_dev.ip_address,
        "last_active": db_dev.last_active
    }

@app.post("/devices/connect", response_model=schemas.DeviceRead)
def connect_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    # 1. Simulate Connection delay/check (mock)
    import time
    # time.sleep(1) 

    # 2. Create Device Entry
    db_device = models.LinkedDevice(
        user_id=device.user_id,
        device_name=device.device_name,
        device_type=device.device_type,
        session_status="connected",
        qr_last_generated=datetime.utcnow(),
        ip_address="192.168.1.1", # Mock IP
        last_active=datetime.utcnow()
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return map_db_device_to_schema(db_device)

@app.get("/devices", response_model=List[schemas.DeviceRead])
def read_devices(user_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.LinkedDevice)
    if user_id:
        query = query.filter(models.LinkedDevice.user_id == user_id)
    
    devices = query.order_by(models.LinkedDevice.last_active.desc()).offset(skip).limit(limit).all()
    return [map_db_device_to_schema(d) for d in devices]

@app.delete("/devices/{device_id}")
def disconnect_device(device_id: str, db: Session = Depends(get_db)):
    device = db.query(models.LinkedDevice).filter(models.LinkedDevice.device_id == device_id).first()
    if not device:
         raise HTTPException(status_code=404, detail="Device not found")
            
    db.delete(device)
    db.commit()
    return {"message": "Device disconnected successfully"}

# --- Session Routes ---

import secrets

def map_db_session_to_schema(db_sess: models.DeviceSession):
    return {
        "session_id": db_sess.session_id,
        "device_id": db_sess.device_id,
        "session_token": db_sess.session_token,
        "is_valid": db_sess.is_valid,
        "created_at": db_sess.created_at,
        "expires_at": db_sess.expires_at
    }

@app.post("/sessions", response_model=schemas.SessionRead)
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    # 1. Verify Device Exists
    device = db.query(models.LinkedDevice).filter(models.LinkedDevice.device_id == session_data.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # 2. Check if already has active session? (Optional Logic)
    # For now, we allow multiple sessions per device or just create new one
    
    # Generate Token
    token = secrets.token_urlsafe(32)

    db_session = models.DeviceSession(
        device_id=session_data.device_id,
        session_token=token,
        is_valid="true"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return map_db_session_to_schema(db_session)

@app.get("/sessions/validate")
def validate_session(token: str, db: Session = Depends(get_db)):
    session = db.query(models.DeviceSession).filter(models.DeviceSession.session_token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if session.is_valid != "true":
         raise HTTPException(status_code=401, detail="Session invalid")
    
    if session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Session expired")
        
    return {"status": "valid", "device_id": session.device_id}

# --- Usage Log Routes ---

def map_db_log_to_schema(db_log: models.UsageLog):
    return {
        "usage_id": db_log.usage_id,
        "user_id": db_log.user_id,
        "message_id": db_log.message_id,
        "credits_deducted": db_log.credits_deducted,
        "balance_after": db_log.balance_after,
        "timestamp": db_log.timestamp
    }

@app.get("/usage/logs", response_model=List[schemas.UsageLogRead])
def read_usage_logs(user_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.UsageLog)
    if user_id:
        query = query.filter(models.UsageLog.user_id == user_id)
    
    logs = query.order_by(models.UsageLog.timestamp.desc()).offset(skip).limit(limit).all()
    return [map_db_log_to_schema(l) for l in logs]
