"""
Dependency injection functions for the application.
Provides database sessions with user context for row-level security.
"""
from fastapi import Depends
from app.core.base_deps import get_db_session
from app.models.models import User
from app.core.auth import get_current_active_user
from app.db.session import get_db

def get_user_db(current_user: User = Depends(get_current_active_user)):
    """
    Database session with user ID for row-level security.
    
    Args:
        current_user: Currently authenticated user
        
    Yields:
        Database session with user context
    """
    db = next(get_db(user_type="normal", user_id=current_user.id))
    try:
        yield db
    finally:
        db.close()
