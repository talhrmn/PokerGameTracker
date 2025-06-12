import logging
from datetime import UTC, datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserInput, UserDBInput, UserDBOutput, UserStats, MonthlyStats
from app.services.base import BaseService


class UserService(BaseService[UserInput, UserDBOutput]):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_user_by_username(self, username: str) -> Optional[UserDBOutput]:
        return await self.repository.get_by_username(username)

    async def get_user_by_email(self, email: str) -> Optional[UserDBOutput]:
        return await self.repository.get_by_email(email)

    async def create_user(self, user_data: UserInput) -> Optional[UserDBOutput]:
        # Check uniqueness
        exists = await self.repository.get_by_username(user_data.username)
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        exists = await self.repository.get_by_email(str(user_data.email))
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        # Hash password
        password_hash = get_password_hash(user_data.password)
        user_input = UserDBInput(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            last_login=datetime.now(UTC),
            # other fields (profile_pic defaults to None, created_at default, etc.)
        )
        # Use base create:
        try:
            created = await self.repository.create(user_input)
            return created
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation failed")

    # Other methods unchanged, calling specialized repository methods:
    async def update_login(self, user_id: str) -> UserDBOutput:
        return await self.repository.update_login(user_id)

    async def update_user_data(self, user_id: str, update_data: dict) -> Optional[UserDBOutput]:
        if "username" in update_data:
            existing = await self.repository.get_by_username(update_data["username"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        if "email" in update_data:
            existing = await self.repository.get_by_email(update_data["email"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
        return await self.repository.update(user_id, update_data)

    async def update_user_stats(self, user_id: str, user_inc: UserStats) -> Optional[UserDBOutput]:
        return await self.repository.increment_user_stats(user_id, user_inc)

    async def get_user_monthly_stats(self, user_id: str) -> Optional[List[MonthlyStats]]:
        monthly_stats = await self.repository.get_user_monthly_stats(user_id)
        return [MonthlyStats(**stats) for stats in monthly_stats]

    async def update_user_monthly_stats(self, user_id: str, month: str, user_inc: MonthlyStats) -> Optional[
        UserDBOutput]:
        ok = await self.repository.upsert_monthly_stats(user_id, month, user_inc)
        if not ok:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to update monthly stats")

    async def get_user_friends(self, user_id: str) -> Optional[List[UserDBOutput]]:
        friends = await self.repository.get_user_friends(user_id)
        return friends

    async def get_user_invited_friends(self, user_id: str) -> Optional[List[UserDBOutput]]:
        return await self.repository.get_user_invited_friends(user_id)

    async def add_friend(self, user_id: str, friend_id: str) -> None:
        if not ObjectId.is_valid(friend_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid friend ID")
        friend = await self.repository.get_by_id(friend_id)
        if not friend:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend user not found")
        await self.repository.add_friend(user_id, friend_id)

    async def remove_friend(self, user_id: str, friend_id: str) -> None:
        if not ObjectId.is_valid(friend_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid friend ID")
        await self.repository.remove_friend(user_id, friend_id)

    async def search_users(self, user_id: str, friend_regex: str) -> List[UserDBOutput]:
        return await self.repository.search_users(user_id, friend_regex)

    async def update_win_rate(self, user_id: str, stats: dict):
        total_games = stats.get("total_games", 0)
        win_rate = (stats["wins"] / total_games) * 100 if total_games > 0 else 0.0
        await self.update(user_id, {"stats.win_rate": win_rate})

    async def update_monthly_win_rates(self, user_id: str, stats: List[dict]):
        for month_data in stats:
            month_str = month_data["_id"]
            wins = month_data.get("wins", 0)
            total = month_data.get("total_games", 0)
            month_win_rate = (wins / total) * 100 if total > 0 else 0.0
            await self.repository.update_monthly_stats(user_id, month_str, month_win_rate)
