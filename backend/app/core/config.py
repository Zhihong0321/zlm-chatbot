from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    ZAI_API_KEY: str
    DATABASE_URL: str  # PRODUCTION: MUST be PostgreSQL
    CORS_ORIGINS: list[str] = ["*"]
    
    # Production settings
    ENVIRONMENT: str = "production"  # Force production on Railway
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()