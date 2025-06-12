import logging
from typing import Dict, List, Optional, Union

from app.core.exceptions import DatabaseError, ResourceNotFoundError
from app.core.security import get_password_hash
from app.repositories.user import UserRepository
from app.schemas.user import MonthlyStats, UserDBResponse, UserCreate, UserStats
from bson import ObjectId

from app.services.base import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService):
    def __init__(self, db_client):
        super().__init__(UserRepository(db_client))

    async def get_user_by_username(self, username: str) -> Optional[UserDBResponse]:
        user = await self.repository.get_by_username(username)
        if not user:
            logger.info(f"User not found with username: {username}")
        return user

    async def get_user_by_email(self, email: str) -> Optional[UserDBResponse]:
        user = await self.repository.get_by_email(email)
        if not user:
            logger.info(f"User not found with email: {email}")
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[UserDBResponse]:
        user = await self.repository.get_by_id(user_id)
        if not user:
            logger.info(f"User not found with id: {user_id}")
            raise ResourceNotFoundError("User", user_id)
        return user

    async def create_user(self, user_data: UserCreate) -> UserDBResponse:
        try:
            hashed_password = get_password_hash(user_data.password)
            user_dict = user_data.dict()
            user_dict["password_hash"] = hashed_password
            del user_dict["password"]
            return await self.repository.create_user(user_dict)
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise DatabaseError(f"Failed to create user: {str(e)}")

    async def update_login(self, user_id: str) -> None:
        try:
            await self.repository.update_login(user_id)
        except Exception as e:
            logger.error(f"Failed to update login time for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to update login time: {str(e)}")

    async def update_user_data(self, user_id: ObjectId, update_data: Dict) -> None:
        if not update_data:
            logger.warning(f"No update data provided for user {user_id}")
            return

        try:
            await self.repository.update_user_data(user_id, update_data)
        except Exception as e:
            logger.error(f"Failed to update user data for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to update user data: {str(e)}")

    async def update_user_stats(
        self, user_id: str, user_inc: Union[UserStats, MonthlyStats], stats_type: str
    ) -> None:
        try:
            await self.repository.update_user_stats(user_id, user_inc, stats_type)
        except Exception as e:
            logger.error(f"Failed to update user stats for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to update user stats: {str(e)}")

    async def update_user_monthly_stats(
        self, user_id: str, month: str, user_inc: MonthlyStats
    ) -> None:
        try:
            await self.repository.update_user_monthly_stats(user_id, month, user_inc)
            await self.repository.update_win_rates(user_id)
        except Exception as e:
            logger.error(f"Failed to update monthly stats for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to update monthly stats: {str(e)}")

    async def get_user_friends(self, user_id: str) -> List[UserDBResponse]:
        try:
            return await self.repository.get_user_friends(user_id)
        except Exception as e:
            logger.error(f"Failed to get friends for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to get friends: {str(e)}")

    async def get_user_invited_friends(self, user_id: str) -> List[UserDBResponse]:
        try:
            return await self.repository.get_user_invited_friends(user_id)
        except Exception as e:
            logger.error(f"Failed to get invited friends for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to get invited friends: {str(e)}")

    async def update_friends(self, user_id: ObjectId, friend_id: ObjectId) -> None:
        try:
            await self.repository.update_friends(user_id, friend_id)
        except Exception as e:
            logger.error(
                f"Failed to update friends for users {user_id} and {friend_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to update friends: {str(e)}")

    async def remove_friends(self, user_id: ObjectId, friend_id: ObjectId) -> None:
        try:
            await self.repository.remove_friends(user_id, friend_id)
        except Exception as e:
            logger.error(
                f"Failed to remove friends for users {user_id} and {friend_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to remove friends: {str(e)}")

    async def search_user(self, user_id: ObjectId, friend_regex: str) -> List[UserDBResponse]:
        try:
            return await self.repository.search_user(user_id, friend_regex)
        except Exception as e:
            logger.error(f"Failed to search users with regex {friend_regex}: {str(e)}")
            raise DatabaseError(f"Failed to search users: {str(e)}")
