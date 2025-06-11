from datetime import timedelta

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.security import create_access_token
from app.handlers.users import user_handler
from app.schemas.auth import LoginResponse
from app.schemas.py_object_id import PyObjectId
from app.schemas.user import UserDBResponse


class AuthHandler:

    def __init__(self):
        pass

    async def login_user(cls, user: UserDBResponse, db_client: AsyncIOMotorClient) -> LoginResponse:
        await user_handler.update_login(user=user, db_client=db_client)
        access_token = cls.create_access_token(user.id)
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
        )

    @staticmethod
    def create_access_token(user_id: PyObjectId):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=access_token_expires
        )
        return access_token


auth_handler = AuthHandler()
