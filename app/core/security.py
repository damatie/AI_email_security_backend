# Security Utils - app/core/security.py

import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Token creation utility
def create_verification_token(email: str) -> str:
    """
    Generate a JWT token for email verification.
    Includes the email as the subject (sub) and sets an expiration time.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_verification_token(token: str) -> str:
    """
    Decode and verify the email verification token.
    Raises exceptions if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise ValueError("Verification token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid verification token.")

# Access token creation for authentication
def create_access_token(data: dict, secret_key: str, expires_delta: timedelta = None) -> str:
    """
    Generate a JWT token with expiration.
    """
    # Ensure expires_delta is properly calculated
    try:
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        )
    except ValueError as e:
        raise ValueError("Invalid ACCESS_TOKEN_EXPIRE_MINUTES in settings. It must be an integer.") from e

    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    """
    Decode and verify the JWT access token.
    Raises exceptions if the token is invalid or expired.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Access token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid access token.")
