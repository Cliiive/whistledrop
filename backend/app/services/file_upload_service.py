"""
File upload and encryption service.
Handles secure file storage with AES-GCM encryption and RSA key protection.
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import UUID
from ..models.models import SymmetricalKey, File, User, PublicKey
import uuid
import os
from fastapi import UploadFile
from app.core.config import settings
from PyPDF2 import PdfReader, PdfWriter
import io, os

class EncryptedFileResult(BaseModel):
    """
    Result model for an encrypted file operation.
    Contains the encrypted data and related encryption parameters.
    """
    file_name: str
    ciphertext: bytes
    nonce: bytes
    key: bytes


def encrypt_pdf(file: UploadFile) -> EncryptedFileResult:
    """
    Encrypt a PDF file using AES-GCM.

    Args:
        file: Uploaded file to encrypt

    Returns:
        EncryptedFileResult containing ciphertext and encryption parameters
    """
    key = AESGCM.generate_key(256)
    aesgcm = AESGCM(key)

    # Read uploaded file into memory (nur einmal lesen)
    original_bytes = file.file.read()

    # Step 1: Remove metadata safely using PyPDF2
    input_pdf = PdfReader(io.BytesIO(original_bytes))
    output_pdf = PdfWriter()

    for page in input_pdf.pages:
        output_pdf.add_page(page)

    output_pdf.add_metadata({})  # remove all metadata

    # Step 2: Write cleaned PDF to memory
    cleaned_pdf_io = io.BytesIO()
    output_pdf.write(cleaned_pdf_io)
    cleaned_pdf_io.seek(0)
    cleaned_bytes = cleaned_pdf_io.read()

    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, cleaned_bytes, associated_data=None)

    return EncryptedFileResult(
        file_name=file.filename,
        ciphertext=ciphertext,
        nonce=nonce,
        key=key
    )

def save_encrypted_file(db: Session, file_name: str, ciphertext: bytes, user_id: UUID, symetricla_key_id: UUID) -> UUID:
    """
    Save an encrypted file to storage and record in database.
    
    Args:
        db: Database session
        file_name: Name of the file
        ciphertext: Encrypted file content
        user_id: ID of the file owner
        symetricla_key_id: ID of the associated symmetric key
        
    Returns:
        UUID of the created file record
    """
    file_name = file_name.split(".")[0] + "_encrypted"
    file_path = os.path.join(settings.FILE_PATH, file_name)

    db_file = File(id=uuid.uuid4(),
                   user_id=user_id,
                   symetrical_key_id=symetricla_key_id,
                   path=file_path,
                   file_name=file_name,
                   content_type="application/pdf",
                   seen=False
                   )

    # Save the encrypted file to the database
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    counter = 0
    new_file_path = file_path
    while os.path.exists(new_file_path):
        counter += 1
        name, ext = os.path.splitext(file_path)
        new_file_path = f"{name}_{counter}{ext}"

    if new_file_path != file_path:
        db_file.path = new_file_path
        db.commit()
        file_path = new_file_path

    # Write file to storage
    with open(file_path, "wb") as f:
        f.write(ciphertext)

    print(f"File saved at {file_path}")

    return db_file.id

def save_aesgcm_key(db: Session, aes_key: bytes, public_key_id: UUID, nonce: bytes) -> UUID:
    """
    Save an AES-GCM key to the database.
    
    Args:
        db: Database session
        aes_key: Encrypted AES key
        public_key_id: ID of the public key used for encryption
        nonce: Initialization vector used with AES-GCM
        
    Returns:
        UUID of the created symmetric key record
    """
    # Save the AESGCM key securely
    db_key = SymmetricalKey(key=aes_key, public_key_id=public_key_id, nonce=nonce)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    print(f"Key saved with ID {db_key.id}")
    return db_key.id


def encrypt_aes_key(db: Session, aes_key: bytes) -> tuple[bytes, UUID]:
    """
    Encrypt an AES key with a public RSA key.
    
    Args:
        db: Database session
        aes_key: AES key to encrypt
        
    Returns:
        Tuple of (encrypted key, public key ID)
        
    Raises:
        Exception: If no active public key is available
    """
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from base64 import b64encode

    # Get the next active public key
    pub_key: PublicKey = db.query(PublicKey).filter(PublicKey.active == True).first()

    if not pub_key:
        raise Exception("Due to high usage of the system, uploading files is currently not possible. Please try again later.")
    # Mark the public key as inactive
    pub_key.active = False
    db.commit()
    db.refresh(pub_key)

    # Deserialize the public key
    public_key = load_pem_public_key(pub_key.key)

    # Encrypt the AES key with the public RSA key
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encode the encrypted key as Base64 for storage
    encrypted_key_b64 = b64encode(encrypted_key)

    return encrypted_key_b64, pub_key.id

def allowed_type(file: UploadFile) -> bool:
    """
    Check if the uploaded file type is allowed.
    
    Args:
        file: Uploaded file to check
        
    Returns:
        Boolean indicating if the file type is allowed
    """
    # Check if the file is a PDF
    if file.content_type != "application/pdf":
        print("Invalid file type. Only PDF files are allowed.")
        return False
    return True

# only for testing purposes
def insert_random_user(db: Session) -> UUID:
    """
    Insert a random test user into the database.
    For testing purposes only.
    
    Args:
        db: Database session
        
    Returns:
        UUID of the created test user
    """
    # Insert a random user into the database
    # This is a placeholder for the actual user insertion logic
    # You would use a user creation function here
    user = User(alias="test_user")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Inserted random user with ID {user.id}")
    return user.id


