# Security Utils - app/core/security.py

import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from passlib.context import CryptContext

# Hash pappword
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#Create  email verification token
def create_verification_token(email: str) -> str:
    """
    Generate a JWT token for email verification.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes= settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# Email verification token
def decode_verification_token(token: str) -> str:
    """
    Decode and verify the email verification token.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise ValueError("Verification token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid verification token.")