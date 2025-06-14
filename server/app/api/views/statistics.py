from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_user,
    get_game_service,
    get_table_service,
    get_statistics_service
)
from app.core.exceptions import NotFoundException
from app.schemas.statistics import DashboardStats, StatisticsDBOutput
from app.schemas.user import UserResponse
from app.services.game_service import GameService
from app.services.statistics_service import StatisticsService
from app.services.table_service import TableService

router = APIRouter()


@router.get("/", response_model=StatisticsDBOutput)
async def get_user_stats(
        current_user: UserResponse = Depends(get_current_user),
        statistics_service: StatisticsService = Depends(get_statistics_service)):
    """
    Get monthly statistics for the current user.

    Args:
        current_user: The current authenticated user
        statistics_service: The statistics service

    Returns:
        List of monthly statistics

    Raises:
        DatabaseException: If the database operation fails
    """
    res = await statistics_service.get_all_user_stats(str(current_user.id))
    return res


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service),
        table_service: TableService = Depends(get_table_service),
        statistics_service: StatisticsService = Depends(get_statistics_service)
) -> DashboardStats:
    """
    Get dashboard statistics for the current user.
    
    Args:
        current_user: The current authenticated user
        game_service: The game service
        table_service: The table service
        statistics_service: The statistics service
        
    Returns:
        Dashboard statistics including user stats, monthly changes, and recent games
        
    Raises:
        NotFoundException: If the user is not found
        DatabaseException: If any database operation fails
    """
    user_stats = await statistics_service.get_all_user_stats(str(current_user.id))
    if not user_stats:
        raise NotFoundException(detail="User stats not found")

    recent_games = await game_service.get_recent_games(current_user, 5)

    formatted_games = []
    for game in recent_games:
        table = await table_service.get_by_id(str(game.table_id))
        recent_game_stats = statistics_service.get_formatted_recent_game(current_user.id, game, table)
        formatted_games.append(recent_game_stats)

    user_monthly_changes = statistics_service.get_user_monthly_change_stats(user_stats)

    return DashboardStats(
        user_stats=user_stats.stats,
        monthly_changes=user_monthly_changes,
        recent_games=formatted_games
    )
