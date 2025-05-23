"""
Database session management module.
Handles connection setup, user roles, and database initialization.
"""
import uuid

from ..models.models import Base

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.core.security import hash_passphrase
import os
from sqlalchemy import text
load_dotenv()

# Separate connections for different user roles
DATABASE_URL_NORMAL = os.getenv("DATABASE_URL_NORMAL")
DATABASE_URL_ADMIN = os.getenv("DATABASE_URL_ADMIN")

# Separate engines for different access levels
normal_engine = create_engine(DATABASE_URL_NORMAL)
admin_engine = create_engine(DATABASE_URL_ADMIN)

# Separate sessions
NormalSessionLocal = sessionmaker(bind=normal_engine)
AdminSessionLocal = sessionmaker(bind=admin_engine)


def init_db():
    """
    Initialize the database schema, tables, and permissions.
    Creates roles, users, and sets appropriate access levels.
    """
    print("Creating tables and permissions...")

    # Superuser connection for initial setup
    conn = admin_engine.connect()

    try:
        # Reset schema
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()

        # Create tables
        Base.metadata.create_all(bind=admin_engine)

        # Create users and roles
        normal_password = os.getenv("POSTGRES_PASSWORD")
        admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD")

        # Safer: Separate commands for users and roles
        setup_commands = [
            # Create roles
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
            "DROP ROLE IF EXISTS normal_role;",
            "DROP ROLE IF EXISTS admin_role;",
            "CREATE ROLE normal_role;",
            "CREATE ROLE admin_role;",

            # Create or update users
            f"DROP USER IF EXISTS normal_db_user;",
            f"DROP USER IF EXISTS admin_db_user;",
            f"CREATE USER normal_db_user WITH PASSWORD '{normal_password}';",
            f"CREATE USER admin_db_user WITH PASSWORD '{admin_password}';",

            # Assign roles
            "GRANT normal_role TO normal_db_user;",
            "GRANT admin_role TO admin_db_user;",

            # Basic permissions
            "GRANT USAGE ON SCHEMA public TO normal_role, admin_role;",

            # Table access
            "GRANT SELECT, INSERT, UPDATE ON users, files, symmetrical_keys TO normal_role;",
            "GRANT SELECT, INSERT, UPDATE ON public_keys TO normal_role;", # TODO: IMPORTANT IMPORTANT REMOVE INSERT HERE
            "GRANT DELETE ON files TO normal_role;",
            "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;",
            "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO normal_role, admin_role;",
        ]

        for cmd in setup_commands:
            conn.execute(text(cmd))
            conn.commit()

    finally:
        conn.close()

def create_admin_account():
    """
    Create an administrator account in the database.
    Uses the admin password from environment variables.
    """
    conn = admin_engine.connect()

    try:
        # Create admin account
        admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD")
        hashed_password = hash_passphrase(admin_password)
        conn.execute(text(f"INSERT INTO users (id, passphrase_hash, is_admin) VALUES ('{uuid.uuid4()}', '{hashed_password}', true);"))
        conn.commit()
    finally:
        conn.close()

def get_db(user_type="normal", user_id=None):
    """
    Get a database session with appropriate permissions.
    
    Args:
        user_type: Type of user ("normal" or "admin")
        user_id: Optional user ID for context
        
    Yields:
        A database session that will be automatically closed
    """
    if user_type == "admin":
        db = AdminSessionLocal()
    else:
        db = NormalSessionLocal()

    try:
        yield db
    finally:
        db.close()
