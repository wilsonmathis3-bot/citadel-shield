import hashlib
import base64
import secrets

def generate_salt() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode()

def hash_email(email: str) -> str:
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()

def verify_blob_integrity(encrypted_data: bytes, checksum: str) -> bool:
    return hashlib.sha256(encrypted_data).hexdigest() == checksum

def generate_secure_id() -> str:
    return secrets.token_urlsafe(16)
