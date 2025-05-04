from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Boolean, VARCHAR
from sqlalchemy import Column, Integer, LargeBinary

Base = declarative_base()

# Define a model to store the AES key
class EncryptionKey(Base):
    __tablename__ = 'encryption_keys'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    active = Column(Boolean, nullable=False)
    key = Column(LargeBinary, nullable=False)

class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    path = Column(VARCHAR(255), nullable=False)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    alias = Column(VARCHAR(255), nullable=False)