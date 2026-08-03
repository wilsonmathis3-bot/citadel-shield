from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import base64
from app.database import get_db
from app.models import VaultBlob
from app.crypto_utils import verify_blob_integrity, generate_secure_id
from app.config import get_settings
from jose import jwt, JWTError

router = APIRouter(prefix="/vault", tags=["vault"])
settings = get_settings()

class VaultSyncRequest(BaseModel):
    encrypted_data: str
    nonce: str
    checksum: str
    version: Optional[int] = 1

class VaultSyncResponse(BaseModel):
    status: str
    version: int
    updated_at: str

async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/sync", response_model=VaultSyncResponse)
async def sync_vault(req: VaultSyncRequest, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    encrypted_bytes = base64.b64decode(req.encrypted_data)
    if not verify_blob_integrity(encrypted_bytes, req.checksum):
        raise HTTPException(status_code=400, detail="Integrity check failed")
    result = await db.execute(select(VaultBlob).where(VaultBlob.user_id == user_id))
    vault = result.scalar_one_or_none()
    if vault:
        vault.encrypted_data = encrypted_bytes
        vault.nonce = req.nonce
        vault.checksum = req.checksum
        vault.version = req.version
    else:
        vault = VaultBlob(id=generate_secure_id(), user_id=user_id, encrypted_data=encrypted_bytes, nonce=req.nonce, checksum=req.checksum, version=req.version)
        db.add(vault)
    await db.commit()
    return VaultSyncResponse(status="synced", version=vault.version, updated_at=str(vault.updated_at))

@router.get("/fetch")
async def fetch_vault(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VaultBlob).where(VaultBlob.user_id == user_id))
    vault = result.scalar_one_or_none()
    if not vault:
        return {"exists": False, "encrypted_data": None}
    return {"exists": True, "encrypted_data": base64.b64encode(vault.encrypted_data).decode(), "nonce": vault.nonce, "checksum": vault.checksum, "version": vault.version, "updated_at": str(vault.updated_at)}
