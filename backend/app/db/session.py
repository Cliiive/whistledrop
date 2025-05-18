import uuid

from ..models.models import Base

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.core.security import hash_passphrase
import os

load_dotenv()

# Separate Verbindungen für verschiedene Benutzerrollen
DATABASE_URL_NORMAL = os.getenv("DATABASE_URL_NORMAL")
DATABASE_URL_ADMIN = os.getenv("DATABASE_URL_ADMIN")

# Separate Engines für unterschiedliche Zugriffslevel
normal_engine = create_engine(DATABASE_URL_NORMAL)
admin_engine = create_engine(DATABASE_URL_ADMIN)

# Separate Sessions
NormalSessionLocal = sessionmaker(bind=normal_engine)
AdminSessionLocal = sessionmaker(bind=admin_engine)


def init_db():
    """Tabellen und Berechtigungen einrichten"""
    print("Creating tables and permissions...")

    # Superuser-Verbindung zur initialen Einrichtung
    conn = admin_engine.connect()

    try:
        # Schema zurücksetzen
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()

        # Tabellen erstellen
        Base.metadata.create_all(bind=admin_engine)

        # Benutzer und Rollen erstellen
        normal_password = os.getenv("POSTGRES_PASSWORD")
        admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD")

        # Sicherer: Separate Befehle für Benutzer und Rollen
        setup_commands = [
            # Rollen erstellen
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
            "DROP ROLE IF EXISTS normal_role;",
            "DROP ROLE IF EXISTS admin_role;",
            "CREATE ROLE normal_role;",
            "CREATE ROLE admin_role;",

            # Benutzer erstellen oder aktualisieren
            f"DROP USER IF EXISTS normal_db_user;",
            f"DROP USER IF EXISTS admin_db_user;",
            f"CREATE USER normal_db_user WITH PASSWORD '{normal_password}';",
            f"CREATE USER admin_db_user WITH PASSWORD '{admin_password}';",

            # Rollen zuweisen
            "GRANT normal_role TO normal_db_user;",
            "GRANT admin_role TO admin_db_user;",

            # Grundberechtigungen
            "GRANT USAGE ON SCHEMA public TO normal_role, admin_role;",

            # Tabellenzugriff
            "GRANT SELECT, INSERT, UPDATE ON users, files, symmetrical_keys TO normal_role;",
            "GRANT SELECT, INSERT ON public_keys TO normal_role;", # TODO: IMPORTANT IMPORTANT REMOVE INSERT HERE
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
    """Admin-Account erstellen"""
    conn = admin_engine.connect()

    try:
        # Admin-Account erstellen
        admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD")
        hashed_password = hash_passphrase(admin_password)
        conn.execute(text(f"INSERT INTO users (id, passphrase_hash, is_admin) VALUES ('{uuid.uuid4()}', '{hashed_password}', true);"))
        conn.commit()
    finally:
        conn.close()

def get_db(user_type="normal", user_id=None):
    """DB-Session mit entsprechenden Berechtigungen holen."""
    if user_type == "admin":
        db = AdminSessionLocal()
    else:
        db = NormalSessionLocal()

    try:
        yield db
    finally:
        db.close()