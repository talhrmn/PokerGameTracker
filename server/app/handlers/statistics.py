from typing import List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.schemas.user import UserResponse, MonthlyStats


class StatisticsHandler:

    def __init__(self):
        pass

    @staticmethod
    async def get_monthly_statistics(user: UserResponse, db_client: AsyncIOMotorClient) -> List[MonthlyStats]:
        user_monthly_stats = await db_client.users.find_one({"_id": ObjectId(user.id)}, {"monthly_stats": 1})
        if not user_monthly_stats:
            return []
        return [MonthlyStats(**stats) for stats in user_monthly_stats.get("monthly_stats")]


statistics_handler = StatisticsHandler()
