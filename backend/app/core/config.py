from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # MongoDB (use env var if available, fallback to default)
    MONGO_URI: str = "mongodb+srv://aniketbedwal90_db_user:aniketbedwal90_db_user@cluster0.jw3kv6t.mongodb.net/skillgap_v3?retryWrites=true&w=majority"
    MONGO_DB_NAME: str = "skillgap_v3"
    PORT: int = 8000

    # AI APIs
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Auth
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://skill-gap-seven.vercel.app",
    ]

    # ML Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    NER_MODEL: str = "en_core_web_sm"

    # AI Reliability
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 2

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()