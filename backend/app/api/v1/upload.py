from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.file_upload_service import encrypt_pdf, save_aesgcm_key, encrypt_aes_key, save_encrypted_file
from app.services.file_upload_service import allowed_type
from app.services.file_remove_service import delete_file_from_db, delete_file_from_storage
from app.core.dependencies import get_user_db
from app.core.dependencies import get_db_session
from app.models.models import User
import app.models.models as db_models
from app.core.auth import get_current_active_user
from app.core.exceptions import FileTypeNotAllowed
from app.db.session import get_db
router = APIRouter()

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_user_db) # type: ignore
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

    file_id: UUID = save_encrypted_file(db, result.file_name, result.ciphertext, current_user.id, aes_key_id)

    return {"message": "success"}

# return a list of files the user has uploaded
@router.get("/")
async def get_files(
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_active_user)
):
    files = db.query(db_models.File).filter(db_models.File.user_id == current_user.id).all()
    return files

@router.delete("/{id}")
async def delete_file(
    id: UUID,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if the file exists
    file: File = db.query(db_models.File).filter(db_models.File.id == id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    # Check if the file belongs to the current user
    if file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this file"
        )

    # Delete the file from the database
    if not delete_file_from_db(db, id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file from database"
        )

    if not delete_file_from_storage(str(file.path)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file from storage"
        )

    return {
        "message": "File deleted successfully"
    }

