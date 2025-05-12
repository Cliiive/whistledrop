from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy import UUID
from sqlalchemy.orm import Session
from app.services.file_upload_service import encrypt_pdf, save_aesgcm_key, encrypt_aes_key, save_encrypted_file
from app.services.file_upload_service import allowed_type
from app.core.dependencies import get_db_session
from app.models.models import User
import app.models.models as db_models
from app.core.auth import get_current_active_user
from app.core.exceptions import FileTypeNotAllowed
router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    # Check if the file type is allowed
    if not allowed_type(file):
        raise FileTypeNotAllowed()

    # Check if the file size is within the limit

    # TODO: Error handling -> what if the pdf is saved but the key is not?
    # handle encryption + storage
    result = encrypt_pdf(file)
    encrypted_key, public_key_id = encrypt_aes_key(db, result.key)
    aes_key_id = save_aesgcm_key(db, encrypted_key, public_key_id, result.nonce)

    save_encrypted_file(db, result.file_name, result.ciphertext, current_user.id, aes_key_id)

    return {"message": "success"}

# return a list of files the user has uploaded
@router.get("/")
async def get_files(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    files = db.query(db_models.File).filter(db_models.File.user_id == current_user.id).all()
    return files
