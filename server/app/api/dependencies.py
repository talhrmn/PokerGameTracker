from fastapi import Request, Depends, HTTPException
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status

from app.core.config import settings
from app.core.security import oauth2_scheme
from app.db.mongo_client import MongoDB
from app.repositories.game_repository import GameRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.repositories.table_repository import TableRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.friends_service import FriendsService
from app.services.game_service import GameService
from app.services.sse_service import SSEService
from app.services.statistics_service import StatisticsService
from app.services.table_service import TableService
from app.services.user_service import UserService


def get_database():
    return MongoDB.db


def get_user_repository(db_client: AsyncIOMotorClient = Depends(get_database)) -> UserRepository:
    return UserRepository(db_client)


def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           user_service: UserService = Depends(get_user_service),
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

    user = await user_service.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    return UserResponse(**user.model_dump())


def get_table_repository(db_client: AsyncIOMotorClient = Depends(get_database)) -> TableRepository:
    return TableRepository(db_client)


def get_table_service(table_repo: TableRepository = Depends(get_table_repository)) -> TableService:
    return TableService(table_repo)


def get_game_repository(db_client: AsyncIOMotorClient = Depends(get_database)) -> GameRepository:
    return GameRepository(db_client)


def get_game_service(game_repo: GameRepository = Depends(get_game_repository)) -> GameService:
    return GameService(game_repo)


def get_statistics_repository(db_client: AsyncIOMotorClient = Depends(get_database)) -> StatisticsRepository:
    return StatisticsRepository(db_client)


def get_statistics_service(stats_repo: StatisticsRepository = Depends(get_statistics_repository)) -> StatisticsService:
    return StatisticsService(stats_repo)


def get_auth_service() -> AuthService:
    return AuthService(settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def get_sse_service(
        request: Request,
        table_service: TableService = Depends(get_table_service),
        game_service: GameService = Depends(get_game_service),
) -> SSEService:
    app = request.app
    if not hasattr(app.state, "sse_service"):
        app.state.sse_service = SSEService(table_service=table_service, game_service=game_service)
    return app.state.sse_service


def get_friends_service() -> FriendsService:
    return FriendsService()
