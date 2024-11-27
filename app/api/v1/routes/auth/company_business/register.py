# app/api/v1/routes/auth/company_register.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.auth.company_business.register import RegisterNewCompanyRequest, RegisterNewCompanyResponse
from app.models import User, Role
from app.core.security import get_password_hash
from app.utils.enums import RoleEnum, UserStatusEnum

router = APIRouter()

@router.post("/", response_model=RegisterNewCompanyResponse, status_code=status.HTTP_201_CREATED)
async def register_company(
    company_data: RegisterNewCompanyRequest,
    db: Session = Depends(get_db),
):
    """
    Company admin registration endpoint.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == company_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # Assign the COMPANY_ADMIN role
    role = db.query(Role).filter(Role.name == RoleEnum.COMPANY_ADMIN).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="COMPANY_ADMIN role is not configured.",
        )

    # Hash the admin's password
    hashed_password = get_password_hash(company_data.password)

    # Create a new admin
    new_admin = User(
        email=company_data.email,
        password_hash=hashed_password,
        is_admin=True,
        role_id=role.id,
        status=UserStatusEnum.PENDING,
        onboarding_completed=False,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {
        "message": "Company admin registered successfully. Proceed to onboarding.",
        "admin_id": new_admin.id,
    }
