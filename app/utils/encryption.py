# app/utils/encryption.py
from cryptography.fernet import Fernet
from app.core.config import settings

ENCRYPTION_KEY = settings.ENCRYPTION_KEY
fernet = Fernet(ENCRYPTION_KEY)


def encrypt_token(token: str) -> str:
    """
    Encrypts a token using Fernet symmetric encryption.
    """
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypts an encrypted token using Fernet symmetric encryption.
    """
    return fernet.decrypt(encrypted_token.encode()).decode()
