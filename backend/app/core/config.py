"""
Application configuration settings.
Uses environment variables with defaults.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Provides configuration for database, authentication, API, and storage.
    """
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL_NORMAL")

    # Authentication settings
    AUTH_SECRET: str = os.getenv("AUTH_SECRET")
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # API settings
    API_PREFIX: str = "/api/v1"

    # Storage path
    FILE_PATH: str = "/app/storage/uploads/"  # Path to save the uploaded files

    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
