from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


async def connect_to_mongo():
    MongoDB.client = AsyncIOMotorClient(settings.MONGODB_URL, tz_aware=True)
    MongoDB.db = MongoDB.client[settings.MONGODB_DB_NAME]


async def close_mongo_connection():
    if MongoDB.client:
        MongoDB.client.close()
