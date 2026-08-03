from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import User
from app.config import get_settings
from app.crypto_utils import generate_salt, generate_secure_id

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

class RegisterRequest(BaseModel):
    email: EmailStr
    auth_hash: str
    salt: str

class LoginRequest(BaseModel):
    email: EmailStr
    auth_hash: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    salt: str

def create_access_token(user_id: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(id=generate_secure_id(), email=req.email, auth_hash=req.auth_hash, salt=req.salt)
    db.add(user)
    await db.commit()
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id, salt=req.salt)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or user.auth_hash != req.auth_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login = datetime.utcnow()
    await db.commit()
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id, salt=user.salt)
