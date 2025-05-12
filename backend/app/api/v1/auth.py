# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db_session
from app.services.auth_service import authenticate_user, create_user
from pydantic import BaseModel
from app.core.auth import create_access_token

router = APIRouter()


class SeedPhraseRequest(BaseModel):
    seed_phrase: str

@router.post("/login")
async def login(request: SeedPhraseRequest, db: Session = Depends(get_db_session)):
    user = authenticate_user(db, request.seed_phrase)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Seed-Phrase"
        )

    # JWT-Token erstellen
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "message": "Erfolgreich eingeloggt",
        "user_id": str(user.id),
        "alias": user.alias,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/register")
async def register_user(db: Session = Depends(get_db_session)):
    # Erstelle den Benutzer
    user, seed_phrase = create_user(db)

    # JWT-Token erstellen
    access_token = create_access_token(data={"sub": str(user.id)})

    # Wichtig: Die Seed-Phrase wird nur einmal zurückgegeben!
    return {
        "message": "Benutzer erfolgreich erstellt",
        "user_id": str(user.id),
        "seed_phrase": seed_phrase,  # Diese muss der Benutzer sicher aufbewahren
        "access_token": access_token,
        "token_type": "bearer"
    }
