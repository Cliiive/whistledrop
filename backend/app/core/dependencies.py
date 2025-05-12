from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User


def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()