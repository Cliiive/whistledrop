"""
Authentication service for user validation and creation.
Handles passphrase verification and user registration.
"""
from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import verify_passphrase, hash_passphrase, generate_passphrase

import uuid

def authenticate_user(db: Session, passphrase: str):
    """
    Authenticate a user with the provided passphrase.
    
    Args:
        db: Database session
        passphrase: Plaintext passphrase to verify
        
    Returns:
        User object if authenticated, None otherwise
    """
    # Retrieve all users
    users = db.query(User).all()
    for user in users:
        if user.passphrase_hash and verify_passphrase(passphrase, user.passphrase_hash):
            return user

    return None


def create_user(db: Session):
    """
    Create a new user with a generated passphrase.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (user object, plaintext passphrase)
    """
    # Generate a passphrase
    passphrase = generate_passphrase()

    # Create a new user
    user = User(
        id=uuid.uuid4(),
        passphrase_hash=hash_passphrase(passphrase)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Return the user and passphrase
    return user, passphrase
