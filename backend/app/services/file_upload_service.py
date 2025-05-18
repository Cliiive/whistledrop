from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import UUID
from ..models.models import SymmetricalKey, File, User, PublicKey
import uuid
import os
from fastapi import UploadFile
from app.core.config import settings

class EncryptedFileResult(BaseModel):
    file_name: str
    ciphertext: bytes
    nonce: bytes
    key: bytes

def encrypt_pdf(file: UploadFile) -> EncryptedFileResult:
    key = AESGCM.generate_key(256)
    aesgcm = AESGCM(key)
    plaintext = file.file.read()

    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    return EncryptedFileResult(
        file_name=file.filename,
        ciphertext=ciphertext,
        nonce=nonce,
        key=key
    )

def save_encrypted_file(db: Session, file_name: str, ciphertext: bytes, user_id: UUID, symetricla_key_id: UUID) -> UUID:

    file_name = file_name.split(".")[0] + "_encrypted"
    file_path = os.path.join(settings.FILE_PATH, file_name)

    db_file = File(id=uuid.uuid4(),
                   user_id=user_id,
                   symetrical_key_id=symetricla_key_id,
                   path=file_path,
                   file_name=file_name,
                   content_type="application/pdf")

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

    # Datei schreiben
    with open(file_path, "wb") as f:
        f.write(ciphertext)

    print(f"Datei gespeichert unter {file_path}")

    return db_file.id

def save_aesgcm_key(db: Session, aes_key: bytes, public_key_id: UUID, nonce: bytes) -> UUID:
    # Speichere den AESGCM Schlüssel sicher
    db_key = SymmetricalKey(key=aes_key, public_key_id=public_key_id, nonce=nonce)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    print(f"Key saved with ID {db_key.id}")
    return db_key.id


def encrypt_aes_key(db: Session, aes_key: bytes) -> tuple[bytes, UUID]:
    """Verschlüsselt einen AES-Schlüssel mit einem öffentlichen RSA-Schlüssel."""
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from base64 import b64encode

    # Hole den nächsten aktiven öffentlichen Schlüssel
    pub_key: PublicKey = db.query(PublicKey).filter(PublicKey.active == True).first()

    # Markiere den öffentlichen Schlüssel als inaktiv
    pub_key.active = False
    db.commit()
    db.refresh(pub_key)

    # Deserialisiere den öffentlichen Schlüssel
    public_key = load_pem_public_key(pub_key.key)

    # Verschlüssele den AES-Schlüssel mit dem öffentlichen RSA-Schlüssel
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Kodiere den verschlüsselten Schlüssel als Base64 für die Speicherung
    encrypted_key_b64 = b64encode(encrypted_key)

    return encrypted_key_b64, pub_key.id

def allowed_type(file: UploadFile) -> bool:
    # Check if the file is a PDF
    if file.content_type != "application/pdf":
        print("Invalid file type. Only PDF files are allowed.")
        return False
    return True

# only for testing purposes
def insert_random_user(db: Session) -> UUID:
    # Insert a random user into the database
    # This is a placeholder for the actual user insertion logic
    # You would use a user creation function here
    user = User(alias="test_user")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Inserted random user with ID {user.id}")
    return user.id
