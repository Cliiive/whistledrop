# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import verify_seed_phrase, hash_seed_phrase, generate_seed_phrase

import uuid

def authenticate_user(db: Session, seed_phrase: str):
    """Authentifiziert einen Benutzer anhand der Seed-Phrase."""
    # Alle Benutzer abrufen
    users = db.query(User).all()
    print(users.__len__())
    for user in users:
        print(user.phrase_hash)
        if user.phrase_hash and verify_seed_phrase(seed_phrase, user.phrase_hash):
            return user

    return None


def create_user(db: Session):
    """Erstellt einen neuen Benutzer mit einer generierten Seed-Phrase."""
    # Generiere eine Seed-Phrase
    seed_phrase = generate_seed_phrase()

    # Erstelle einen neuen Benutzer
    user = User(
        id=uuid.uuid4(),
        phrase_hash=hash_seed_phrase(seed_phrase)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Gib den Benutzer und die Seed-Phrase zurück
    return user, seed_phrase