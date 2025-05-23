"""
Core dependency functions for database session management.
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

def get_db_session():
    """
    FastAPI dependency that provides a database session and handles cleanup.
    
    Yields:
        Database session object that will be automatically closed after request
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
