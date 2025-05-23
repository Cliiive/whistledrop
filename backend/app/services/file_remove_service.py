"""
File removal service for deleting uploaded files.
Handles both database record deletion and file system cleanup.
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import UUID
from ..models.models import SymmetricalKey, File, User, PublicKey
import uuid
import os
from fastapi import UploadFile

def delete_file_from_storage(file_path: str):
    """
    Delete a file from the file system.
    
    Args:
        file_path: Path to the file to be deleted
        
    Returns:
        Boolean indicating success or failure
    """
    print(file_path)
    print(os.path.exists("/app"))
    try:
        os.remove(file_path)
        return True
    except OSError as e:
        return False

def delete_file_from_db(db: Session, file_id: UUID):
    """
    Delete a file record from the database.
    
    Args:
        db: Database session
        file_id: UUID of the file to delete
        
    Returns:
        Boolean indicating success or failure
    """
    db_file = db.query(File).filter(File.id == file_id).first()

    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    else:
        return False
