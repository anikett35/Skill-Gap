from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    global _client, _db
    _client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize=20,
        minPoolSize=2,
        serverSelectionTimeoutMS=5000,
    )
    _db = _client[settings.MONGO_DB_NAME]

    # Create indexes
    await _db.users.create_index("email", unique=True)
    await _db.analyses.create_index("user_id")
    await _db.analyses.create_index("created_at")
    await _db.progress.create_index("user_id", unique=True)
    await _db.chat_history.create_index([("user_id", 1), ("analysis_id", 1)])

    logger.info(f"Connected to MongoDB: {settings.MONGO_DB_NAME}")


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
