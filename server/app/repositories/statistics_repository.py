import logging
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.exceptions import DatabaseException
from app.repositories.base import BaseRepository
from app.schemas.statistics import StatisticsDBOutput, StatisticsBase, MonthlyStats, Stats


class StatisticsRepository(BaseRepository[StatisticsBase, StatisticsDBOutput]):
    """
    Repository for statistics collection.

    This repository handles all database operations related to user statistics, including:
    - User CRUD operations (inherited from BaseRepository)
    - User statistics and monthly stats

    Type Parameters:
        StatisticsBase: Pydantic model for user creation/updates
        StatisticsDBOutput: Pydantic model for user responses
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        """
        Initialize the user repository.

        Args:
            db_client: MongoDB client instance
        """
        super().__init__(db_client.statistics, StatisticsBase, StatisticsDBOutput)
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_all_user_stats(self, user_id: str) -> Optional[StatisticsDBOutput]:
        """
        Get a user's statistics.

        Args:
            user_id: The ID of the user

        Returns:
            Optional[UserDBOutput]: The user's monthly stats if found, None otherwise

        Raises:
            DatabaseException: If there's an error fetching the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            query = {"user_id": ObjectId(user_id)}
            return await self.get_one_by_query(query)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get monthly stats: {str(e)}")

    async def increment_user_stats(self, user_id: str, user_inc: Stats) -> Optional[StatisticsDBOutput]:
        """
        Increment a user's statistics.

        Args:
            user_id: The ID of the user to update
            user_inc: The statistics to increment

        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise

        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            inc_dict = {f"stats.{key}": value for key, value in user_inc.model_dump().items()}
            result = await self.collection.update_one(
                {"user_id": ObjectId(user_id)},
                {"$inc": inc_dict}
            )
            if not result.acknowledged:
                raise DatabaseException(detail="Failed to update user stats")
            return await self.get_by_id(user_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update user stats: {str(e)}")

    async def upsert_monthly_stats(self, user_id: str, month: str, user_inc: MonthlyStats) -> Optional[
        StatisticsDBOutput]:
        """
        Update or insert monthly statistics for a user.

        Args:
            user_id: The ID of the user
            month: The month to update stats for
            user_inc: The statistics to update

        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise

        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            user_query = {"user_id": ObjectId(user_id), "monthly_stats.month": month}
            projection = {"monthly_stats.$": 1}
            found = await self.collection.get_one_by_query(user_query, projection, dump_model=False)
            if found and found.get("monthly_stats"):
                update_fields = ["profit", "tables_played", "hours_played"]
                inc_dict = {
                    f"monthly_stats.$.{key}": getattr(user_inc, key)
                    for key in update_fields
                    if getattr(user_inc, key, None) is not None
                }
                if not inc_dict:
                    return None
                result = await self.collection.update_one(user_query, {"$inc": inc_dict})
            else:
                data = user_inc.model_dump()
                result = await self.collection.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$push": {"monthly_stats": data}}
                )
            if not result.acknowledged:
                raise DatabaseException(detail="Failed to update monthly stats")
            return await self.get_by_id(user_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update monthly stats: {str(e)}")

    async def update_monthly_stats(self, user_id: str, month_str: str, month_win_rate: float) -> None:
        """
        Update a user's monthly win rate.

        Args:
            user_id: The ID of the user
            month_str: The month to update
            month_win_rate: The new win rate

        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise DatabaseException(detail="Invalid user ID")
            result = await self.collection.update_one(
                {"user_id": ObjectId(user_id), "monthly_stats.month": month_str},
                {"$set": {"monthly_stats.$.win_rate": month_win_rate}}
            )
            if not result.acknowledged:
                raise DatabaseException(detail="Failed to update monthly win rate")
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update monthly win rate: {str(e)}")
