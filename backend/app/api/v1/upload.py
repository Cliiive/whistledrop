from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy import UUID
from sqlalchemy.orm import Session
from app.services.file_upload_handler import encrypt_pdf, save_aesgcm_key, encrypt_aes_key, save_encrypted_file
from app.services.file_upload_handler import allowed_type
from app.db.session import get_db

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check if the file type is allowed
    if not allowed_type(file):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File type not allowed"
        )

    # Check if the file size is within the limit

    # TODO: Error handling -> what if the pdf is saved but the key is not?
    # handle encryption + storage
    result = encrypt_pdf(file)
    file_id: UUID = save_encrypted_file(db, result.file_name, result.ciphertext)

    encrypted_key = encrypt_aes_key(result.key)

    save_aesgcm_key(db, encrypted_key, file_id, result.nonce)
    # handle saving the file to the database
    save_aesgcm_key(db, result.key, file_id, result.nonce)
    return {"message": "success"}
