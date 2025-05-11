from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import UUID
from ..models.models import SymmetricalKey, File
import uuid
import os

from fastapi import UploadFile
FILE_PATH = "/app/storage/uploads/"  # Path to save the uploaded files

class EncryptedFileResult(BaseModel):
    file_name: str
    ciphertext: bytes
    nonce: bytes
    key: bytes

def gen_aesgcm() -> AESGCM:
    # Generates a cryptographically secure 256-bit key
    key: bytes = AESGCM.generate_key(256)
    print("New aesgcm key generated")
    return AESGCM(key)

def encrypt_pdf(file: UploadFile) -> EncryptedFileResult:
    key = AESGCM.generate_key(256)
    aesgcm = AESGCM(key)

    plain_data = file.read()
    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, plain_data, associated_data=None)

    return EncryptedFileResult(
        file_name=file.filename,
        ciphertext=ciphertext,
        nonce=nonce,
        key=key
    )

def save_encrypted_file(db: Session, file_name: str, ciphertext: bytes) -> UUID:
    file_path = os.path.join(FILE_PATH, file_name)

    # TODO: Uses a raondom UUID for the user_id, replace with actual user_id
    db_file = File(user_id=uuid.uuid4(), path=file_path, file_name=file_name, content_type="application/pdf")

    # Save the encrypted file to the database
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    with open(file_path, "wb") as f:
        f.write(ciphertext)

    print(f"File saved to {file_path}")

    return db_file.id

def save_aesgcm_key(db: Session, aes_key: bytes, file_id: UUID, nonce: bytes) -> None:
    # Speichere den AESGCM Schlüssel sicher
    db_key = SymmetricalKey(key=aes_key, file_id=file_id, nonce=nonce)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    print(f"AESGCM key saved for file ID {file_id}")


def encrypt_aes_key(aes_key: bytes) -> bytes:
    # Encrypt the AES key with the public key
    # This is a placeholder for the actual encryption logic
    # You would use a public key encryption algorithm here
    return aes_key  # Replace with actual encrypted key

