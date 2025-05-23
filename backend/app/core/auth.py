"""
Authentication module for JWT token generation and validation.
Provides functions to create and verify access tokens for users.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.base_deps import get_db_session
from app.models.models import User
from app.core.config import settings
import os


# OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token for authentication.
    
    Args:
        data: Data to encode into the token (typically includes user ID)
        expires_delta: Optional expiration time delta, defaults to settings value
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.AUTH_SECRET, algorithm=settings.AUTH_ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db_session)) -> User:
    """
    Get the current user from a JWT token.
    
    Args:
        token: JWT token string
        db: Database session
        
    Returns:
        User object if authentication is successful
        
    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.AUTH_SECRET, algorithms=[settings.AUTH_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    Currently just passes through the user without checking active status.
    
    Args:
        current_user: User object from get_current_user
        
    Returns:
        User object if active
        
    Raises:
        HTTPException: If user is not active (commented out currently)
    """
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Inactive user",
    #     )
    return current_user
