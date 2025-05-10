from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Boolean, VARCHAR
from sqlalchemy import Column, Integer, LargeBinary

Base = declarative_base()

# Define a model to store the AES key
class SymmetricalKey(Base):
    __tablename__ = 'symmetrical_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    key = Column(LargeBinary, nullable=False)

class PublicKey(Base):
    __tablename__ = 'public_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False)
    key = Column(LargeBinary, nullable=False)

class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    path = Column(VARCHAR(255), nullable=False)
    file_name = Column(VARCHAR(255), nullable=False)
    content_type = Column(VARCHAR(100), nullable=False)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(VARCHAR(255), nullable=False)