from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator
from typing import List
import json


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017/?serverSelectionTimeoutMS=5000"
    MONGO_DB_NAME: str = "skillgap_v3"
    PORT: int = 8000

    # AI APIs
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Auth
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS — stored as plain str to avoid pydantic-settings JSON parsing errors.
    # Accepts comma-separated: "http://localhost:3000,https://example.com"
    # Also accepts JSON array: '["http://localhost:3000","https://example.com"]'
    # If blank/missing in .env, the property below returns the safe default list.
    ALLOWED_ORIGINS_STR: str = ""

    # ML Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    NER_MODEL: str = "en_core_web_sm"

    # AI Reliability
    AI_TIMEOUT_SECONDS: int = 120
    AI_MAX_RETRIES: int = 2

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse ALLOWED_ORIGINS_STR into a list at runtime — never crashes."""
        default = [
            "http://localhost:3000",
            "http://localhost:5173",
            "https://skill-gap-seven.vercel.app",
            "https://skill-gap-mtzv.onrender.com",
        ]
        raw = (self.ALLOWED_ORIGINS_STR or "").strip()
        if not raw:
            return default
        # Try JSON array first: ["url1","url2"]
        if raw.startswith("["):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated: url1,url2,url3
        return [o.strip() for o in raw.split(",") if o.strip()]

    @model_validator(mode='after')
    def validate_env(self):
        import logging
        logger = logging.getLogger(__name__)
        if not self.GROQ_API_KEY and not self.ANTHROPIC_API_KEY:
            logger.warning("No AI API keys set - AI features disabled")
        if 'localhost' not in self.MONGO_URI and '127.0.0.1' not in self.MONGO_URI:
            logger.warning(f"Using remote MongoDB - ensure IP is whitelisted in Atlas")
        else:
            logger.info("Using local MongoDB")
        logger.info(f"CORS will allow: {self.ALLOWED_ORIGINS}")
        return self


settings = Settings()