# app/api/v1/routes/auth/verify_email.py

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models import User
from app.db.deps import get_db
from app.core.security import decode_verification_token
from app.utils.enums import  UserStatusEnum

verify_email_router = APIRouter()

@verify_email_router.get("/verify_email/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify the user's email address using the token.
    """
    # Fetch the user by token
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or token invalid.",
        )

    if user.status == UserStatusEnum.ACTIVE:
        return {"message": "Email is already verified."}

    try:
        # Decode the token to ensure it is valid and not expired
        decode_verification_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Mark the email as verified
    user.status = UserStatusEnum.ACTIVE
    user.verification_token = None  # Clear the token after successful verification
    db.commit()

    return {"message": "Email verified successfully."}
