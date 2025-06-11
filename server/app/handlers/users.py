from datetime import datetime, UTC
from typing import Union, Dict, Optional

from bson import ObjectId
from fastapi import HTTPException, status as status_code
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.security import get_password_hash
from app.schemas.game import GameStatusEnum
from app.schemas.user import UserCreate, UserDBInput, UserStats, MonthlyStats, UserDBResponse


class UserHandler:

    def __init__(self):
        pass

    @staticmethod
    async def get_user_by_id(user_id: str, db_client: AsyncIOMotorClient) -> Optional[UserDBResponse]:
        user = await db_client.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return UserDBResponse(**user)

    @staticmethod
    async def get_user_by_username(username: str, db_client: AsyncIOMotorClient) -> Optional[UserDBResponse]:
        user = await db_client.users.find_one({"username": username})
        if not user:
            return None
        return UserDBResponse(**user)

    @staticmethod
    async def get_user_by_email(email: str, db_client: AsyncIOMotorClient) -> Optional[UserDBResponse]:
        user = await db_client.users.find_one({"email": email})
        if not user:
            return None
        return UserDBResponse(**user)

    @staticmethod
    async def create_user(user_data: UserCreate, db_client: AsyncIOMotorClient) -> UserDBResponse:
        new_user = UserDBInput(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        ).model_dump()
        result = await db_client.users.insert_one(new_user)

        if not (result.acknowledged and result.inserted_id):
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )
        return await UserHandler.get_user_by_id(result.inserted_id, db_client)

    @staticmethod
    async def update_login(user: UserDBResponse, db_client: AsyncIOMotorClient) -> None:
        await db_client.users.update_one(
            {"_id": user.id},
            {"$set": {"last_login": datetime.now(UTC)}}
        )

    @staticmethod
    async def update_user_data(user_id: ObjectId, update_data: Dict, db_client: AsyncIOMotorClient) -> None:
        if update_data:
            result = await db_client.users.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            if not (result.acknowledged and result.inserted_id):
                raise HTTPException(
                    status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database update failed."
                )

    @staticmethod
    async def update_user_stats(user_id: str, user_inc: Union[UserStats, MonthlyStats], stats_type: str,
                                db_client: AsyncIOMotorClient) -> None:
        update_inc = {f"stats.{key}": value for key, value in user_inc.model_dump().items()}
        result = await db_client.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": update_inc}
        )
        if not result.acknowledged:
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )

    async def update_user_monthly_stats(self, user_id: str, month: str, user_inc: MonthlyStats,
                                        db_client: AsyncIOMotorClient) -> None:
        user_query = {"_id": ObjectId(user_id), "monthly_stats.month": month}
        user = await db_client.users.find_one(
            user_query,
            {"monthly_stats.$": 1}
        )

        if user and user.get("monthly_stats"):
            update_fields = ["profit", "tables_played", "hours_played"]
            update_inc = {f"monthly_stats.$.{key}": value for key, value in user_inc.model_dump().items() if
                          key in update_fields}
            result = await db_client.users.update_one(
                user_query,
                {"$inc": update_inc}
            )
        else:
            result = await db_client.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {
                    "monthly_stats": user_inc.model_dump()
                }}
            )

        if not result.acknowledged:
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )
        await self.update_win_rates(user_id=user_id, db_client=db_client)

    @staticmethod
    async def update_win_rates(user_id: str, db_client: AsyncIOMotorClient) -> None:
        pipeline = [
            {"$match": {
                "players.user_id": ObjectId(user_id),
                "status": GameStatusEnum.COMPLETED
            }},
            {"$unwind": "$players"},
            {"$match": {"players.user_id": ObjectId(user_id)}},
            {"$group": {
                "_id": None,
                "wins": {"$sum": {"$cond": [{"$gt": ["$players.net_profit", 0]}, 1, 0]}},
                "total_games": {"$sum": 1}
            }}
        ]

        result = await db_client.games.aggregate(pipeline).to_list(length=1)

        if result:
            stats = result[0]
            win_rate = (stats["wins"] / stats["total_games"]) * 100

            await db_client.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"stats.win_rate": win_rate}}
            )

            pipeline = [
                {"$match": {
                    "players.user_id": ObjectId(user_id),
                    "status": GameStatusEnum.COMPLETED
                }},
                {"$unwind": "$players"},
                {"$match": {"players.user_id": ObjectId(user_id)}},
                {"$group": {
                    "_id": {"$substr": ["$date", 0, 7]},  # Group by YYYY-MM
                    "wins": {"$sum": {"$cond": [{"$gt": ["$players.net_profit", 0]}, 1, 0]}},
                    "total_games": {"$sum": 1}
                }}
            ]

            monthly_results = await db_client.games.aggregate(pipeline).to_list(length=100)

            for month_data in monthly_results:
                month = month_data["_id"]
                month_win_rate = (month_data["wins"] / month_data["total_games"]) * 100

                await db_client.users.update_one(
                    {"_id": ObjectId(user_id), "monthly_stats.month": month},
                    {"$set": {"monthly_stats.$.win_rate": month_win_rate}}
                )

    @staticmethod
    async def get_user_friends(user_id: str, db_client: AsyncIOMotorClient):
        user = await db_client.users.find_one({"_id": ObjectId(user_id)}, {"friends": 1})

        if not user or not user.get("friends"):
            return []

        friends_cursor = db_client.users.find(
            {"_id": {"$in": [ObjectId(friend) for friend in user.get("friends", [])]}})
        friends = await friends_cursor.to_list(length=100)
        for friend in friends:
            if "password_hash" in friend:
                del friend["password_hash"]
        return friends

    @staticmethod
    async def get_user_invited_friends(user_id: str, db_client: AsyncIOMotorClient):
        users = await db_client.users.find({"friends": user_id}).to_list(None)  # Fix here

        if not users:
            return []

        for user in users:
            user.pop("password_hash", None)

        return users

    @staticmethod
    async def update_friends(user_id: ObjectId, friend_id: ObjectId, db_client: AsyncIOMotorClient):
        await db_client.users.update_one(
            {"_id": user_id, "friends": {"$ne": friend_id}},
            {"$push": {"friends": friend_id}}
        )

        await db_client.users.update_one(
            {"_id": friend_id, "friends": {"$ne": user_id}},
            {"$push": {"friends": user_id}}
        )

    @staticmethod
    async def remove_friends(user_id: ObjectId, friend_id: ObjectId, db_client: AsyncIOMotorClient):
        await db_client.users.update_one(
            {"_id": user_id},
            {"$pull": {"friends": friend_id}}
        )

        await db_client.users.update_one(
            {"_id": friend_id},
            {"$pull": {"friends": user_id}}
        )

    @staticmethod
    async def search_user(user_id: ObjectId, friend_regex: str, db_client: AsyncIOMotorClient):

        cursor = db_client.users.find(
            {
                "_id": {"$ne": user_id},
                "username": {"$regex": friend_regex, "$options": "i"},
                "email": {"$regex": friend_regex, "$options": "i"}
            },
            {
                "password_hash": 0
            }
        ).limit(10)

        users = await cursor.to_list(length=10)
        return users


user_handler = UserHandler()
