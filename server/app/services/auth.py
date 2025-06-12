import logging
from datetime import timedelta
from typing import Optional

from app.core.config import settings
from app.core.exceptions import DatabaseError
from app.core.security import create_access_token
from app.schemas.auth import LoginResponse
from app.schemas.py_object_id import PyObjectId
from app.schemas.user import UserDBResponse
from app.services.user import UserService
from app.services.base import BaseService
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    def __init__(
        self,
        db_client: AsyncIOMotorClient,
        user_service: UserService,
    ):
        super().__init__(db_client)
        self.user_service = user_service

    async def login_user(self, user: UserDBResponse) -> LoginResponse:
        try:
            # Update last login time
            await self.user_service.update_login(user.id)

            # Create access token
            access_token = self.create_access_token(user.id)

            logger.info(f"User {user.username} logged in successfully")
            return LoginResponse(
                access_token=access_token, token_type="bearer", user=user
            )
        except Exception as e:
            logger.error(f"Login failed for user {user.username}: {str(e)}")
            raise DatabaseError(f"Login failed: {str(e)}")

    @staticmethod
    def create_access_token(user_id: PyObjectId):
        try:
            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"sub": str(user_id)}, expires_delta=access_token_expires
            )
            return access_token
        except Exception as e:
            logger.error(f"Failed to create access token for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to create access token: {str(e)}")
