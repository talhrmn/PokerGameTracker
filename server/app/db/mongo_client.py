from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.exceptions import DatabaseException


class MongoDB:
    """
    MongoDB connection manager.
    
    This class manages the MongoDB client and database connection.
    It provides a singleton instance for accessing the database throughout the application.
    
    Attributes:
        client: The MongoDB client instance
        db: The MongoDB database instance
    """
    client: Optional[AsyncIOMotorClient] = None
    db = None


async def connect_to_mongo() -> None:
    """
    Establish connection to MongoDB.
    
    This function initializes the MongoDB client and database connection
    using the configuration from settings.
    
    Raises:
        DatabaseException: If connection to MongoDB fails
    """
    try:
        MongoDB.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tz_aware=True,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        MongoDB.db = MongoDB.client[settings.MONGODB_DB_NAME]

        # Verify connection
        await MongoDB.client.admin.command('ping')
    except Exception as e:
        raise DatabaseException(
            detail=f"Failed to connect to MongoDB: {str(e)}"
        )


async def close_mongo_connection() -> None:
    """
    Close the MongoDB connection.
    
    This function safely closes the MongoDB client connection
    if it exists.
    """
    if MongoDB.client:
        try:
            MongoDB.client.close()
        except Exception as e:
            raise DatabaseException(
                detail=f"Failed to close MongoDB connection: {str(e)}"
            )
