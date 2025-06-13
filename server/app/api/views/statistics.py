from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_user,
    get_user_service,
    get_game_service,
    get_table_service,
    get_statistics_service
)
from app.core.exceptions import NotFoundException
from app.schemas.dash_stats import DashboardStats
from app.schemas.user import UserResponse, MonthlyStats, UserStats
from app.services.game_service import GameService
from app.services.statistics_service import StatisticsService
from app.services.table_service import TableService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/monthly", response_model=List[MonthlyStats])
async def get_monthly_stats(
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> List[MonthlyStats]:
    """
    Get monthly statistics for the current user.
    
    Args:
        current_user: The current authenticated user
        user_service: The user service
        
    Returns:
        List of monthly statistics
        
    Raises:
        DatabaseException: If the database operation fails
    """
    return await user_service.get_user_monthly_stats(str(current_user.id))


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    game_service: GameService = Depends(get_game_service),
    table_service: TableService = Depends(get_table_service),
    statistics_service: StatisticsService = Depends(get_statistics_service)
) -> DashboardStats:
    """
    Get dashboard statistics for the current user.
    
    Args:
        current_user: The current authenticated user
        user_service: The user service
        game_service: The game service
        table_service: The table service
        statistics_service: The statistics service
        
    Returns:
        Dashboard statistics including user stats, monthly changes, and recent games
        
    Raises:
        NotFoundException: If the user is not found
        DatabaseException: If any database operation fails
    """
    user = await user_service.get_by_id(str(current_user.id))
    if not user:
        raise NotFoundException(detail="User not found")

    recent_games = await game_service.get_recent_games(current_user, 5)

    formatted_games = []
    for game in recent_games:
        table = await table_service.get_by_id(str(game.table_id))
        recent_game_stats = statistics_service.get_formatted_recent_game(current_user.id, game, table)
        formatted_games.append(recent_game_stats)

    user_monthly_changes = statistics_service.get_user_monthly_change_stats(user)

    return DashboardStats(
        user_stats=UserStats(
            total_profit=user.stats.total_profit,
            win_rate=user.stats.win_rate,
            tables_played=user.stats.tables_played,
            hours_played=user.stats.hours_played
        ),
        monthly_changes=user_monthly_changes,
        recent_games=formatted_games
    )
