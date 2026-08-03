from sqlalchemy import Column, String, DateTime, LargeBinary, Integer, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    auth_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    kdf_params = Column(JSON, default={"iterations": 600000, "algorithm": "pbkdf2+argon2id"})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class VaultBlob(Base):
    __tablename__ = "vault_blobs"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    encrypted_data = Column(LargeBinary, nullable=False)
    nonce = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    checksum = Column(String(255), nullable=False)

class BreachRecord(Base):
    __tablename__ = "breach_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_hash = Column(String(64), index=True)
    breach_name = Column(String(255))
    breached_date = Column(DateTime(timezone=True))
    data_classes = Column(JSON)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class ThreatIOC(Base):
    __tablename__ = "threat_iocs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ioc_type = Column(String(50), index=True)
    value = Column(String(512), nullable=False, index=True)
    threat_score = Column(Integer, default=0)
    source = Column(String(100))
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
