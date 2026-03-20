from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "skillgap_v3"

    # AI APIs
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Auth
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://your-app.vercel.app",
    ]

    # ML Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    NER_MODEL: str = "en_core_web_sm"

    # AI Reliability
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 2

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
