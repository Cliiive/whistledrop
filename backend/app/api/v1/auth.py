# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.base_deps import get_db_session
from app.services.auth_service import authenticate_user, create_user
from pydantic import BaseModel
from app.core.auth import create_access_token

router = APIRouter()


class PassphraseRequest(BaseModel):
    passphrase: str

@router.post("/login")
async def login(request: PassphraseRequest, db: Session = Depends(get_db_session)):
    user = authenticate_user(db, request.passphrase)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Passphrase"
        )

    # JWT-Token erstellen
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "message": "Erfolgreich eingeloggt",
        "user_id": str(user.id),
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/register")
async def register_user(db: Session = Depends(get_db_session)):
    # Erstelle den Benutzer
    user, passphrase = create_user(db)

    # JWT-Token erstellen
    access_token = create_access_token(data={"sub": str(user.id)})

    # Wichtig: Die Seed-Phrase wird nur einmal zurückgegeben!
    return {
        "message": "Benutzer erfolgreich erstellt",
        "user_id": str(user.id),
        "passphrase": passphrase,  # Diese muss der Benutzer sicher aufbewahren
        "access_token": access_token,
        "token_type": "bearer"
    }
