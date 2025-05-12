# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import verify_passphrase, hash_passphrase, generate_passphrase

import uuid

def authenticate_user(db: Session, passphrase: str):
    # Alle Benutzer abrufen
    users = db.query(User).all()
    for user in users:
        if user.passphrase_hash and verify_passphrase(passphrase, user.passphrase_hash):
            return user

    return None


def create_user(db: Session):
    """Erstellt einen neuen Benutzer mit einer generierten Seed-Phrase."""
    # Generiere eine Seed-Phrase
    passphrase = generate_passphrase()

    # Erstelle einen neuen Benutzer
    user = User(
        id=uuid.uuid4(),
        passphrase_hash=hash_passphrase(passphrase)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Gib den Benutzer und die passphrase zurück
    return user, passphrase