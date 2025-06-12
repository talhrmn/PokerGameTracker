import logging
from typing import Optional

from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_mongo(cls):
        try:
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=settings.MONGODB_MAX_CONNECTIONS,
                minPoolSize=settings.MONGODB_MIN_CONNECTIONS,
                maxIdleTimeMS=settings.MONGODB_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=5000,
                tz_aware=True,
            )
            # Verify the connection
            await cls.client.admin.command("ping")
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info("Successfully connected to MongoDB")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed")

    @classmethod
    async def health_check(cls) -> bool:
        try:
            if not cls.client:
                return False
            await cls.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False


# Initialize connection functions
connect_to_mongo = MongoDB.connect_to_mongo
close_mongo_connection = MongoDB.close_mongo_connection
health_check = MongoDB.health_check


def get_db_client() -> AsyncIOMotorClient:
    """Get the MongoDB client instance."""
    if not MongoDB.client:
        raise RuntimeError("MongoDB client not initialized")
    return MongoDB.client
