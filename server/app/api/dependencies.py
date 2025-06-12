from typing import Annotated

from app.core.config import settings
from app.core.exceptions import InvalidInputError
from app.core.security import oauth2_scheme
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.services.game import GameService
from app.services.sse import SSEService
from app.services.statistics import StatisticsService
from app.services.table import TableService
from app.services.trends import TrendsService
from app.services.user import UserService
from fastapi import Depends
from jose import JWTError, jwt

from app.db.mongo_client import get_db_client
from app.repositories.game import GameRepository
from app.repositories.table import TableRepository
from app.repositories.user import UserRepository


async def get_game_repository(db_client=Depends(get_db_client)) -> GameRepository:
    """Get game repository instance."""
    return GameRepository(db_client)


async def get_table_repository(db_client=Depends(get_db_client)) -> TableRepository:
    """Get table repository instance."""
    return TableRepository(db_client)


async def get_user_repository(db_client=Depends(get_db_client)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(db_client)


async def get_game_service(
    db_client=Depends(get_db_client),
    table_repository: TableRepository = Depends(get_table_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GameService:
    """Get game service instance."""
    return GameService(
        db_client=db_client,
        table_repository=table_repository,
        user_repository=user_repository,
    )


async def get_table_service(
    db_client=Depends(get_db_client),
    game_repository: GameRepository = Depends(get_game_repository),
) -> TableService:
    """Get table service instance."""
    return TableService(
        db_client=db_client,
        game_repository=game_repository,
    )


async def get_user_service(
    db_client=Depends(get_db_client),
) -> UserService:
    """Get user service instance."""
    return UserService(db_client=db_client)


async def get_auth_service(
    db_client=Depends(get_db_client),
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get auth service instance."""
    return AuthService(
        db_client=db_client,
        user_repository=user_repository,
    )


async def get_trends_service(
    game_service: GameService = Depends(get_game_service),
    table_service: TableService = Depends(get_table_service),
) -> TrendsService:
    """Get trends service instance."""
    return TrendsService(
        game_service=game_service,
        table_service=table_service,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get current user from token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidInputError("Invalid token")
    except JWTError:
        raise InvalidInputError("Invalid token")

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise InvalidInputError("User not found")

    return user
