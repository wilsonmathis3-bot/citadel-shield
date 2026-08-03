from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, VaultBlob, BreachRecord, ThreatIOC

router = APIRouter(prefix="/admin", tags=["admin"])

class DashboardStats(BaseModel):
    total_users: int
    active_users_7d: int
    total_vaults: int
    total_threats_blocked: int
    recent_breaches: int

class UserRecord(BaseModel):
    id: str
    email: str
    created_at: datetime
    last_login: datetime | None
    is_active: bool

@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = (await db.execute(select(func.count()).select_from(User).where(User.last_login >= week_ago))).scalar()
    total_vaults = (await db.execute(select(func.count()).select_from(VaultBlob))).scalar()
    threats = (await db.execute(select(func.count()).select_from(ThreatIOC).where(ThreatIOC.threat_score >= 50))).scalar()
    recent_breaches = (await db.execute(select(func.count()).select_from(BreachRecord).where(BreachRecord.added_at >= week_ago))).scalar()
    return DashboardStats(total_users=total_users, active_users_7d=active_users, total_vaults=total_vaults, total_threats_blocked=threats, recent_breaches=recent_breaches)

@router.get("/users", response_model=List[UserRecord])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit).order_by(User.created_at.desc()))
    return [UserRecord(id=u.id, email=u.email, created_at=u.created_at, last_login=u.last_login, is_active=u.is_active) for u in result.scalars().all()]
