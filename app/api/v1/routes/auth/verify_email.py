# app/api/v1/routes/auth/verify_email.py

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models import User
from app.db.deps import get_db
from app.core.security import decode_verification_token
from app.utils.enums import UserStatusEnum
from app.utils.response_helper import create_response

verify_email_router = APIRouter()

@verify_email_router.get("/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify the user's email address using the token.
    """
    # Fetch the user by token
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_response(
                status="error",
                msg="User not found or token invalid.",
                data=None
            ),
        )

    if user.status == UserStatusEnum.ACTIVE:
        return create_response(
            status="success",
            msg="Email is already verified.",
            data=None
        )

    try:
        # Decode the token to ensure it is valid and not expired
        decode_verification_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                status="error",
                msg=str(e),
                data=None
            ),
        )

    # Mark the email as verified
    user.status = UserStatusEnum.ACTIVE
    user.verification_token = None  # Clear the token after successful verification
    db.commit()

    return create_response(
        status="success",
        msg="Email verified successfully.",
        data={"user_id": user.id}
    )
