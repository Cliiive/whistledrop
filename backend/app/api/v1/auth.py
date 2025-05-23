"""
Authentication API endpoints for user login and registration.
Handles passphrase verification and JWT token generation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.base_deps import get_db_session
from app.services.auth_service import authenticate_user, create_user
from pydantic import BaseModel
from app.core.auth import create_access_token

router = APIRouter()


class PassphraseRequest(BaseModel):
    """Request model for login with passphrase"""
    passphrase: str

@router.post("/login")
async def login(request: PassphraseRequest, db: Session = Depends(get_db_session)):
    """
    Authenticates a user with their passphrase and returns a JWT token.
    
    Args:
        request: Contains the user's passphrase
        db: Database session
        
    Returns:
        Dict containing access token and user information
        
    Raises:
        HTTPException: If passphrase is invalid
    """
    user = authenticate_user(db, request.passphrase)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Passphrase"
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "message": "Login successful",
        "user_id": str(user.id),
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/register")
async def register_user(db: Session = Depends(get_db_session)):
    """
    Creates a new user and returns their passphrase and a JWT token.
    
    Args:
        db: Database session
        
    Returns:
        Dict containing access token, user information, and the one-time passphrase
        
    Note:
        The passphrase is only returned once and must be securely stored by the user
    """
    # Create the user
    user, passphrase = create_user(db)

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Important: The passphrase is only returned once!
    return {
        "message": "User created successfully",
        "user_id": str(user.id),
        "passphrase": passphrase,  # User must securely store this
        "access_token": access_token,
        "token_type": "bearer"
    }
