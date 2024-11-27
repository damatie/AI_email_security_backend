# app/db/init_db.py
from sqlalchemy.orm import Session
from app.models import Role
from app.utils.enums import RoleEnum
from app.utils.permissions import get_default_permissions
from app.db.session import engine
from app.models.base import Base
import logging

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    Initialize the database with necessary tables and default data.
    This function should be called when setting up the application for the first time.
    """
    try:
        # Create all tables defined in your models
        Base.metadata.create_all(bind=engine)
        logger.info("Created database tables")
        
        # Initialize default roles
        init_roles(db)
        logger.info("Initialized default roles")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def init_roles(db: Session) -> None:
    """
    Initialize the default roles in the database.
    This creates SUPER_ADMIN, COMPANY_ADMIN, and USER roles if they don't exist.
    """
    try:
        # Loop through each role type defined in RoleEnum
        for role_enum in RoleEnum:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == role_enum).first()
            
            if not existing_role:
                # Get permissions for this role from our permissions utility
                role_permissions = get_default_permissions(role_enum)
                
                # Create new role
                new_role = Role(
                    name=role_enum,
                    description=f"{role_enum.value} role",
                    permissions=role_permissions  # This is stored as JSON in the database
                )
                
                # Add role to database
                db.add(new_role)
                logger.info(f"Created role: {role_enum.value}")
        
        # Commit all new roles to the database
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing roles: {str(e)}")
        raise