from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Boolean, VARCHAR, UUID, TIMESTAMP, func
from sqlalchemy import Column, Integer, LargeBinary
import uuid
Base = declarative_base()

# Define a model to store the AES key
class SymmetricalKey(Base):
    __tablename__ = 'symmetrical_keys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_key_id = Column(UUID(as_uuid=True), ForeignKey('public_keys.id', ondelete='CASCADE'), nullable=False)
    nonce = Column(LargeBinary, nullable=False) # 'number used once'
    key = Column(LargeBinary, nullable=False)

class PublicKey(Base):
    __tablename__ = 'public_keys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    active = Column(Boolean, nullable=False)
    key = Column(LargeBinary, nullable=False)

class File(Base):
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    symetrical_key_id = Column(UUID(as_uuid=True), ForeignKey('symmetrical_keys.id', ondelete='CASCADE'), nullable=False)
    path = Column(VARCHAR(255), nullable=False)
    file_name = Column(VARCHAR(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    content_type = Column(VARCHAR(100), nullable=False)

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passphrase_hash = Column(VARCHAR(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
