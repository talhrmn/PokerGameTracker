# app/repositories/user_repository.py

import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.repositories.base import BaseRepository
from app.schemas.user import UserDBInput, UserDBOutput, UserStats, MonthlyStats


class UserRepository(BaseRepository[UserDBInput, UserDBOutput]):
    """
    Repository for users collection.
    - Uses UserDBInput for create/insertion.
    - Uses UserDBResponse for read/response.
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client.users, UserDBInput, UserDBOutput)
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_by_username(self, username: str) -> Optional[UserDBOutput]:
        return await self.get_one_by_query({"username": username})

    async def get_by_email(self, email: str) -> Optional[UserDBOutput]:
        return await self.get_one_by_query({"email": email})

    async def update_login(self, user_id: str) -> Optional[UserDBOutput]:
        update_data = {"last_login": datetime.now(UTC)}
        return await self.update(user_id, update_data)

    async def increment_user_stats(self, user_id: str, user_inc: UserStats) -> Optional[UserDBOutput]:
        if not ObjectId.is_valid(user_id):
            raise Exception("")
        inc_dict = {f"stats.{key}": value for key, value in user_inc.model_dump().items()}
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": inc_dict}
        )
        if not result.acknowledged:
            raise Exception("")
        return await self.get_by_id(user_id)

    async def get_user_monthly_stats(self, user_id: str) -> Optional[UserDBOutput]:
        if not ObjectId.is_valid(user_id):
            return None
        query = {"_id": ObjectId(user_id)}
        projection = {"monthly_stats": 1}
        user = await self.get_one_by_query(query, projection, dump_model=False)
        return user.get("monthly_stats")

    async def upsert_monthly_stats(self, user_id: str, month: str, user_inc: MonthlyStats) -> Optional[UserDBOutput]:
        if not ObjectId.is_valid(user_id):
            return None
        user_query = {"_id": ObjectId(user_id), "monthly_stats.month": month}
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
                {"_id": ObjectId(user_id)},
                {"$push": {"monthly_stats": data}}
            )
        if not result.acknowledged:
            raise Exception("")
        return await self.get_by_id(user_id)

    async def update_monthly_stats(self, user_id: str, month_str: str, month_win_rate: float):
        await self.collection.update_one(
            {"_id": ObjectId(user_id), "monthly_stats.month": month_str},
            {"$set": {"monthly_stats.$.win_rate": month_win_rate}}
        )

    async def get_user_friends(self, user_id: str) -> List[UserDBOutput]:
        if not ObjectId.is_valid(user_id):
            return []
        query = {"_id": ObjectId(user_id)}
        projection = {"friends": 1}
        user = await self.get_one_by_query(query, projection, dump_model=False)
        if not user or not user.get("friends"):
            return []
        friend_ids = [ObjectId(fid) for fid in user.get("friends", [])]
        list_filter = {"_id": {"$in": friend_ids}}
        list_projection = {"password_hash": 0}
        friends_list = await self.list(list_filter, list_projection)
        return friends_list

    async def get_user_invited_friends(self, user_id: str) -> List[UserDBOutput]:
        if not ObjectId.is_valid(user_id):
            return []
        list_filter = {"friends": user_id}
        list_projection = {"password_hash": 0}
        friends_list = await self.list(list_filter, list_projection)
        return friends_list

    async def add_friend(self, user_id: str, friend_id: str) -> None:
        if not (ObjectId.is_valid(user_id) and ObjectId.is_valid(friend_id)):
            return
        uid = ObjectId(user_id)
        fid = ObjectId(friend_id)
        await self.collection.update_one(
            {"_id": uid, "friends": {"$ne": fid}},
            {"$push": {"friends": fid}}
        )
        await self.collection.update_one(
            {"_id": fid, "friends": {"$ne": uid}},
            {"$push": {"friends": uid}}
        )

    async def remove_friend(self, user_id: str, friend_id: str) -> None:
        if not (ObjectId.is_valid(user_id) and ObjectId.is_valid(friend_id)):
            return
        uid = ObjectId(user_id)
        fid = ObjectId(friend_id)
        await self.collection.update_one({"_id": uid}, {"$pull": {"friends": fid}})
        await self.collection.update_one({"_id": fid}, {"$pull": {"friends": uid}})

    async def search_users(self, user_id: str, friend_regex: str) -> List[UserDBOutput]:
        if not ObjectId.is_valid(user_id):
            return []
        regex_filter = {"$regex": friend_regex, "$options": "i"}
        list_filter = {
            "_id": {"$ne": ObjectId(user_id)},
            "$or": [
                {"username": regex_filter},
                {"email": regex_filter}
            ]
        }
        list_projection = {"password_hash": 0}
        return await self.list(list_filter, list_projection)
