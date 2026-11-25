import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ViewBox Club Panel System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "viewbox-development-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for dev convenience
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./viewbox.db"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Mock OTP
    MOCK_OTP_DEFAULT: str = "123456"
    OTP_EXPIRY_MINUTES: int = 5
    META_WEBHOOK_SECRET: str | None = None

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
