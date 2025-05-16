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
    Deletes the file at the given path.
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
    Deletes the file from the database.
    """
    db_file = db.query(File).filter(File.id == file_id).first()

    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    else:
        return False