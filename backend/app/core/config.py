from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    ZAI_API_KEY: str
    DATABASE_URL: str = "sqlite:///./chatbot.db"  # Default to SQLite
    CORS_ORIGINS: list[str] = ["*"]
    
    # Production settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


# Force SQLite for local development unless in production
if os.getenv("ENVIRONMENT") != "production":
    os.environ["DATABASE_URL"] = "sqlite:///./chatbot.db"

settings = Settings()