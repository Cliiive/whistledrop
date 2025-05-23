"""
Database models for the application.
Defines the structure of database tables using SQLAlchemy ORM.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Boolean, VARCHAR, UUID, TIMESTAMP, func
from sqlalchemy import Column, Integer, LargeBinary
import uuid
Base = declarative_base()

class SymmetricalKey(Base):
    """
    Model for storing AES encryption keys.
    Each key is associated with a public key used for RSA encryption.
    """
    __tablename__ = 'symmetrical_keys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_key_id = Column(UUID(as_uuid=True), ForeignKey('public_keys.id', ondelete='CASCADE'), nullable=False)
    nonce = Column(LargeBinary, nullable=False)  # Initialization vector for AES-GCM
    key = Column(LargeBinary, nullable=False)    # Encrypted AES key

class PublicKey(Base):
    """
    Model for storing RSA public keys.
    Used to encrypt AES keys for secure file storage.
    """
    __tablename__ = 'public_keys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    active = Column(Boolean, nullable=False)     # Whether this key is available for new encryptions
    key = Column(LargeBinary, nullable=False)    # The PEM-encoded public key

class File(Base):
    """
    Model for storing encrypted file metadata.
    Links to user and encryption key information.
    """
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    symetrical_key_id = Column(UUID(as_uuid=True), ForeignKey('symmetrical_keys.id', ondelete='CASCADE'), nullable=False)
    path = Column(VARCHAR(255), nullable=False)  # Path to stored encrypted file
    file_name = Column(VARCHAR(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    content_type = Column(VARCHAR(100), nullable=False)

class User(Base):
    """
    Model for user accounts.
    Each user authenticates using a passphrase.
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passphrase_hash = Column(VARCHAR(255), nullable=False)  # Hashed passphrase for authentication
    is_admin = Column(Boolean, nullable=False, default=False)  # Admin privileges flag
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
