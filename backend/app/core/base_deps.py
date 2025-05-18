from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()