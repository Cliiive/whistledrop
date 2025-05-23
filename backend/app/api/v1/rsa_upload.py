"""
API endpoint for uploading RSA public keys.
Allows administrators to add public keys that will be used for encryption.
"""
import uuid

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

@router.post("/{id}")
def upload_public_keys(
    id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_user_db) # type: ignore
):
    """
    Upload a public RSA key for file encryption.
    
    Args:
        id: UUID for the public key
        file: The PEM file containing the public key
        current_user: Authenticated user (must be admin)
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user lacks permission or file format is invalid
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload public keys."
        )

    valid_pem_types = ["application/x-pem-file", "application/x-x509-ca-cert",
                       "text/plain", "application/pkcs10"]
    if file.content_type not in valid_pem_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PEM files are allowed. Supported formats: PEM file, X.509 certificate"
        )

    print(id)
    # Insert the key into the public_keys table
    key = db_models.PublicKey(id=id, active=True, key=file.file.read())
    db.add(key)
    db.commit()
    db.refresh(key)

    return {
        "message": "success",
    }
