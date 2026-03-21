from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Initialize MongoDB connection for Atlas srv."""
    global _client, _db
    _client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=20000,
    )
    _db = _client[settings.MONGO_DB_NAME]

    # Create indexes (idempotent)
    await _db.users.create_index("email", unique=True, background=True)
    await _db.analyses.create_index("user_id", background=True)
    await _db.analyses.create_index("created_at", background=True)
    await _db.progress.create_index("user_id", unique=True, background=True)
    await _db.chat_history.create_index([("user_id", 1), ("analysis_id", 1)], background=True)

    try:
        # Test connection
        await _db.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME} ({settings.MONGO_URI.split('@')[0] if '@' in settings.MONGO_URI else settings.MONGO_URI.split('/')[0]})")
    except Exception as e:
        logger.error(f"❌ MongoDB ping failed: {e}")
        raise


async def close_mongo_connection():
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    return _db


# ── Collection helpers ───────────────────────────────────────────────────────

def users_col():
    return _db.users


def analyses_col():
    return _db.analyses


def progress_col():
    return _db.progress


def chat_col():
    return _db.chat_history
