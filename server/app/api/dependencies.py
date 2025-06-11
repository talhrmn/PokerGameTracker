from bson import ObjectId
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status

from server.app.core.config import settings
from server.app.core.security import oauth2_scheme
from server.app.db.mongo_client import MongoDB
from server.app.schemas.user import UserResponse


def get_database():
    return MongoDB.db


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db_client: AsyncIOMotorClient = Depends(get_database)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db_client.users.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise credentials_exception

    return UserResponse(**user)
