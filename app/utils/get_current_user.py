# app/utils/get_current_user.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.db.deps import get_db
from app.models import User
from app.core.security import decode_access_token
from app.utils.response_helper import create_response
import logging

# Configure logger
logger = logging.getLogger(__name__)

# OAuth2 Password Bearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Dependency to retrieve the currently authenticated user based on the JWT token.
    """
    try:
        # Decode the JWT token
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            logger.warning("Authentication failed: Missing subject in token payload.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_response(
                    status="error",
                    msg="Invalid authentication token: Missing subject.",
                    data=None,
                ),
            )
        
        # Find the user in the database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Authentication failed: User with email {email} not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_response(
                    status="error",
                    msg="Authentication failed: User not found.",
                    data=None,
                ),
            )
        
        if not user.is_active:
            logger.warning(f"Authentication failed: User with email {email} is inactive.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=create_response(
                    status="error",
                    msg="User account is inactive. Please contact support.",
                    data=None,
                ),
            )
        
        return user

    except HTTPException:
        raise  # Re-raise known HTTP exceptions
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_response(
                status="error",
                msg="Authentication token is invalid or expired.",
                data=None,
            ),
        )
