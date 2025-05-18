import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Datenbank-Einstellungen
    DATABASE_URL: str = os.getenv("DATABASE_URL_NORMAL")

    # Auth-Einstellungen
    AUTH_SECRET: str = os.getenv("AUTH_SECRET")
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 Tage

    # API-Einstellungen
    API_PREFIX: str = "/api/v1"

    # Storage-Path
    FILE_PATH: str = "/app/storage/uploads/"  # Path to save the uploaded files

    # CORS-Einstellungen
    CORS_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()