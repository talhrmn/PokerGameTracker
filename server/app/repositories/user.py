from datetime import UTC, datetime
from typing import Dict, List, Optional, Union

from app.repositories.base import BaseRepository
from app.schemas.game import GameStatusEnum
from app.schemas.user import MonthlyStats, UserDBResponse, UserStats
from bson import ObjectId


class UserRepository(BaseRepository[UserDBResponse]):
    def __init__(self, db_client):
        super().__init__(db_client, "users")

    async def get_by_username(self, username: str) -> Optional[UserDBResponse]:
        return await self.find_one({"username": username})

    async def get_by_email(self, email: str) -> Optional[UserDBResponse]:
        return await self.find_one({"email": email})

    async def get_by_id(self, user_id: str) -> Optional[UserDBResponse]:
        return await self.find_one({"_id": ObjectId(user_id)})

    async def create_user(self, user_data: dict) -> UserDBResponse:
        return await self.create(user_data)

    async def update_login(self, user_id: str) -> None:
        await self.update({"_id": ObjectId(user_id)}, {"last_login": datetime.now(UTC)})

    async def update_user_data(self, user_id: ObjectId, update_data: Dict) -> None:
        if update_data:
            await self.update({"_id": user_id}, update_data)

    async def update_user_stats(
        self, user_id: str, user_inc: Union[UserStats, MonthlyStats], stats_type: str
    ) -> None:
        update_inc = {
            f"stats.{key}": value for key, value in user_inc.model_dump().items()
        }
        await self.update({"_id": ObjectId(user_id)}, {"$inc": update_inc})

    async def update_user_monthly_stats(
        self, user_id: str, month: str, user_inc: MonthlyStats
    ) -> None:
        user_query = {"_id": ObjectId(user_id), "monthly_stats.month": month}
        user = await self.find_one(user_query, {"monthly_stats.$": 1})

        if user and user.get("monthly_stats"):
            update_fields = ["profit", "tables_played", "hours_played"]
            update_inc = {
                f"monthly_stats.$.{key}": value
                for key, value in user_inc.model_dump().items()
                if key in update_fields
            }
            await self.update(user_query, {"$inc": update_inc})
        else:
            await self.update(
                {"_id": ObjectId(user_id)},
                {"$push": {"monthly_stats": user_inc.model_dump()}},
            )

    async def update_win_rates(self, user_id: str) -> None:
        pipeline = [
            {
                "$match": {
                    "players.user_id": ObjectId(user_id),
                    "status": GameStatusEnum.COMPLETED,
                }
            },
            {"$unwind": "$players"},
            {"$match": {"players.user_id": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": None,
                    "wins": {
                        "$sum": {"$cond": [{"$gt": ["$players.net_profit", 0]}, 1, 0]}
                    },
                    "total_games": {"$sum": 1},
                }
            },
        ]

        result = await self.db_client.games.aggregate(pipeline).to_list(length=1)

        if result:
            stats = result[0]
            win_rate = (stats["wins"] / stats["total_games"]) * 100

            await self.update(
                {"_id": ObjectId(user_id)}, {"$set": {"stats.win_rate": win_rate}}
            )

            pipeline = [
                {
                    "$match": {
                        "players.user_id": ObjectId(user_id),
                        "status": GameStatusEnum.COMPLETED,
                    }
                },
                {"$unwind": "$players"},
                {"$match": {"players.user_id": ObjectId(user_id)}},
                {
                    "$group": {
                        "_id": {"$substr": ["$date", 0, 7]},  # Group by YYYY-MM
                        "wins": {
                            "$sum": {
                                "$cond": [{"$gt": ["$players.net_profit", 0]}, 1, 0]
                            }
                        },
                        "total_games": {"$sum": 1},
                    }
                },
            ]

            monthly_results = await self.db_client.games.aggregate(pipeline).to_list(
                length=100
            )

            for month_data in monthly_results:
                month = month_data["_id"]
                month_win_rate = (month_data["wins"] / month_data["total_games"]) * 100

                await self.update(
                    {"_id": ObjectId(user_id), "monthly_stats.month": month},
                    {"$set": {"monthly_stats.$.win_rate": month_win_rate}},
                )

    async def get_user_friends(self, user_id: str) -> List[UserDBResponse]:
        user = await self.find_one({"_id": ObjectId(user_id)}, {"friends": 1})

        if not user or not user.get("friends"):
            return []

        friends_cursor = self.db_client.users.find(
            {"_id": {"$in": [ObjectId(friend) for friend in user.get("friends", [])]}}
        )
        friends = await friends_cursor.to_list(length=100)
        for friend in friends:
            if "password_hash" in friend:
                del friend["password_hash"]
        return friends

    async def get_user_invited_friends(self, user_id: str) -> List[UserDBResponse]:
        users = await self.db_client.users.find({"friends": user_id}).to_list(None)

        if not users:
            return []

        for user in users:
            user.pop("password_hash", None)

        return users

    async def update_friends(self, user_id: ObjectId, friend_id: ObjectId) -> None:
        await self.update(
            {"_id": user_id, "friends": {"$ne": friend_id}},
            {"$push": {"friends": friend_id}},
        )

        await self.update(
            {"_id": friend_id, "friends": {"$ne": user_id}},
            {"$push": {"friends": user_id}},
        )

    async def remove_friends(self, user_id: ObjectId, friend_id: ObjectId) -> None:
        await self.update({"_id": user_id}, {"$pull": {"friends": friend_id}})

        await self.update({"_id": friend_id}, {"$pull": {"friends": user_id}})

    async def search_user(self, user_id: ObjectId, friend_regex: str) -> List[UserDBResponse]:
        cursor = self.db_client.users.find(
            {
                "_id": {"$ne": user_id},
                "username": {"$regex": friend_regex, "$options": "i"},
                "email": {"$regex": friend_regex, "$options": "i"},
            },
            {"password_hash": 0},
        ).limit(10)

        return await cursor.to_list(length=10)
