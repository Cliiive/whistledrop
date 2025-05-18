from fastapi import Depends
from app.core.base_deps import get_db_session
from app.models.models import User
from app.core.auth import get_current_active_user
from app.db.session import get_db

def get_user_db(current_user: User = Depends(get_current_active_user)):
    """DB-Session mit Benutzer-ID für RLS"""
    db = next(get_db(user_type="normal", user_id=current_user.id))
    try:
        yield db
    finally:
        db.close()