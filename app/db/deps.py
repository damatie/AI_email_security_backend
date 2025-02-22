# app/db/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    finally:
        db.close()