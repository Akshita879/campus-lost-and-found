import datetime
from typing import Optional, Any, Dict
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from app.config import settings

# Configured for fast execution while maintaining Argon2id security
pwd_hasher = PasswordHasher(
    time_cost=1,
    memory_cost=16384,  # 16 MB
    parallelism=1,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return pwd_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2 hash."""
    try:
        return pwd_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(subject: Any, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token. Returns payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
