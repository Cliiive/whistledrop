"""
API endpoints for journalists to download encrypted files.
Provides secure access to whistleblower submissions.
"""
import uuid
from datetime import datetime
import zipfile
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.file_upload_service import encrypt_pdf, save_aesgcm_key, encrypt_aes_key, save_encrypted_file
from app.services.file_upload_service import allowed_type
from app.services.file_remove_service import delete_file_from_db, delete_file_from_storage
from app.core.dependencies import get_user_db
from app.core.dependencies import get_db_session
from app.models.models import User, SymmetricalKey
import app.models.models as db_models
from app.core.auth import get_current_active_user
from app.core.exceptions import FileTypeNotAllowed
from app.db.session import get_db
import io
from typing import Optional


router = APIRouter()

@router.get("/{id}")
async def download_file(
    id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Download a specific encrypted file by ID.
    
    Args:
        id: UUID of the file to download
        db: Database session
        current_user: Authenticated user (must be admin)
        
    Returns:
        The encrypted file with encryption key information in headers
        
    Raises:
        HTTPException: If user lacks permission or file is not found
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download files."
        )

    # Check if the file exists
    file: db_models.File = db.query(db_models.File).filter(db_models.File.id == id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    aes_key: SymmetricalKey = db.query(db_models.SymmetricalKey).filter(db_models.SymmetricalKey.id == file.symetrical_key_id).first()
    # Return the file
    if not aes_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return FileResponse(
        path=file.path,
        filename=file.file_name,
        media_type=file.content_type,
        headers={
            "X-Encrypted-Key": aes_key.key,  # Key in header
            "X-Public-Key-ID": str(aes_key.public_key_id)  # Public Key ID in header
        }
    )

@router.get("/new-files/")
async def download_new_files(
    since_date: str = Query(..., description="ISO formatted date (YYYY-MM-DD)"),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Download all new files since a specified date as a zip archive.
    
    Args:
        since_date: ISO format date string (YYYY-MM-DD)
        db: Database session
        current_user: Authenticated user (must be admin)
        
    Returns:
        Zip file containing all new encrypted files and their key information
        
    Raises:
        HTTPException: If user lacks permission, date format is invalid, or no files found
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download files."
        )
    
    try:
        # Parse date string to datetime
        since_datetime = datetime.fromisoformat(since_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
        )
    
    # Query files created after the specified date
    new_files = db.query(db_models.File).filter(
        db_models.File.created_at > since_datetime
    ).all()
    
    if not new_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No new files found since the specified date"
        )
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in new_files:
            # Get the AES key for the file
            aes_key: SymmetricalKey = db.query(db_models.SymmetricalKey).filter(
                db_models.SymmetricalKey.id == file.symetrical_key_id
            ).first()
            
            if not aes_key:
                continue  # Skip files without keys
            
            # Add the file to the zip archive
            try:
                with open(file.path, 'rb') as f:
                    file_data = f.read()
                    zip_file.writestr(f"{file.id}_{file.file_name}", file_data)
                
                # Add key information in a text file
                key_info = f"Encrypted Key: {aes_key.key}\nNonce: {aes_key.nonce}\nPublic Key ID: {aes_key.public_key_id}"
                zip_file.writestr(f"{file.id}_key_info.txt", key_info)
            except Exception as e:
                # Log the error but continue with other files
                print(f"Error adding file {file.id} to zip: {str(e)}")
    
    # Reset buffer position
    zip_buffer.seek(0)
    
    # Create a filename with the date range
    filename = f"new_files_since_{since_date}.zip"
    
    # Return the zip file
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
