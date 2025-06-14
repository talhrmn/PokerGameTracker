import logging
from datetime import datetime, UTC, timedelta
from typing import Optional, List

from app.core.exceptions import ValidationException, DatabaseException
from app.repositories.statistics_repository import StatisticsRepository
from app.schemas.game import GameDBOutput
from app.schemas.py_object_id import PyObjectId
from app.schemas.statistics import MonthlyChangesStats, RecentGameStats, MonthlyStats, StatisticsDBOutput, Stats, \
    StatisticsBase
from app.schemas.table import TableDBOutput, PlayerStatusEnum
from app.schemas.user import UserDBOutput
from app.services.base import BaseService


class StatisticsService(BaseService[StatisticsBase, StatisticsDBOutput]):
    """
    Service for calculating and formatting user statistics.
    
    This service handles:
    - Monthly statistics calculations and comparisons
    - Recent game statistics formatting
    - Percentage change calculations
    - Data validation and error handling
    
    The service provides methods to:
    - Calculate monthly changes in profit, win rate, tables played, and hours
    - Format recent game statistics for display
    - Handle edge cases and data validation
    """

    def __init__(self, repository: StatisticsRepository):
        """
        Initialize the user service.

        Args:
            repository: StatisticsRepository instance for database operations
        """
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_all_user_stats(self, user_id: str) -> Optional[StatisticsDBOutput]:
        """
        Get a user's statistics.

        Args:
            user_id: The ID of the user

        Returns:
            Optional[StatisticsDBOutput]: User statistics if found, None otherwise

        Raises:
            DatabaseException: If there's an error fetching the stats
        """
        try:
            return await self.repository.get_all_user_stats(user_id)
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to get monthly stats: {str(e)}")
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error getting monthly stats: {str(e)}")

    async def update_user_stats(self, user_id: str, user_inc: Stats) -> Optional[StatisticsDBOutput]:
        """
        Update a user's statistics.

        Args:
            user_id: The ID of the user to update
            user_inc: The statistics to increment

        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise

        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            return await self.repository.increment_user_stats(user_id, user_inc)
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to update user stats: {str(e)}")
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error during stats update: {str(e)}")

    async def update_win_rate(self, user_id: str, stats: dict) -> None:
        """
        Update a user's overall win rate.

        Args:
            user_id: The ID of the user
            stats: Dictionary containing wins and total_games

        Raises:
            DatabaseException: If there's an error updating the win rate
        """
        try:
            total_games = stats.get("total_games", 0)
            win_rate = (stats["wins"] / total_games) * 100 if total_games > 0 else 0.0
            await self.update(user_id, {"stats.win_rate": win_rate})
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update win rate: {str(e)}")

    async def update_monthly_win_rates(self, user_id: str, stats: List[dict]) -> None:
        """
        Update a user's monthly win rates.

        Args:
            user_id: The ID of the user
            stats: List of dictionaries containing monthly statistics

        Raises:
            DatabaseException: If there's an error updating the win rates
        """
        try:
            for month_data in stats:
                month_str = month_data["_id"]
                wins = month_data.get("wins", 0)
                total = month_data.get("total_games", 0)
                month_win_rate = (wins / total) * 100 if total > 0 else 0.0
                await self.repository.update_monthly_stats(user_id, month_str, month_win_rate)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update monthly win rates: {str(e)}")

    async def update_user_monthly_stats(self, user_id: str, month: str, user_inc: MonthlyStats) -> Optional[
        StatisticsDBOutput]:
        """
        Update a user's monthly statistics.

        Args:
            user_id: The ID of the user
            month: The month to update stats for
            user_inc: The statistics to update

        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise

        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            ok = await self.repository.upsert_monthly_stats(user_id, month, user_inc)
            if not ok:
                raise DatabaseException(detail="Failed to update monthly stats")
            return ok
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to update monthly stats: {str(e)}")
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error updating monthly stats: {str(e)}")

    def get_user_monthly_change_stats(self, user_stats: StatisticsDBOutput) -> MonthlyChangesStats:
        """
        Calculate monthly statistics changes for a user_stats.
        
        Args:
            user_stats: The user_stats object containing monthly statistics
            
        Returns:
            MonthlyChangesStats: Object containing formatted percentage changes
            
        Raises:
            ValidationException: If user_stats data is invalid or missing required fields
        """
        try:
            if not user_stats or not hasattr(user_stats, 'monthly_stats'):
                raise ValidationException(detail="Invalid user_stats data")

            current_month = datetime.now(UTC).strftime("%b %Y")
            previous_month = (datetime.now(UTC).replace(day=1) - timedelta(days=1)).strftime("%b %Y")

            current_month_stats = next(
                (stats for stats in user_stats.monthly_stats if stats.month == current_month),
                MonthlyStats(month=current_month)
            )

            previous_month_stats = next(
                (stats for stats in user_stats.monthly_stats if stats.month == previous_month),
                MonthlyStats(month=previous_month)
            )

            profit_change = current_month_stats.profit - previous_month_stats.profit
            win_rate_change = current_month_stats.win_rate - previous_month_stats.win_rate
            tables_change = current_month_stats.tables_played - previous_month_stats.tables_played
            hours_change = current_month_stats.hours_played - previous_month_stats.hours_played

            profit_change_percent = (profit_change / previous_month_stats.profit) * 100 \
                if previous_month_stats.profit else 0
            hours_change_percent = (hours_change / previous_month_stats.hours_played) * 100 \
                if previous_month_stats.hours_played else 0

            format_stat_str = lambda s, d, p: (
                    (f"+{s:.{d}f}" if s > 0 else f"{s:.{d}f}")
                    + ("%" if p else "")
            )

            return MonthlyChangesStats(
                profit_change=format_stat_str(profit_change_percent, "1", True),
                win_rate_change=format_stat_str(win_rate_change, "2", True),
                tables_change=format_stat_str(tables_change, "0", False),
                hours_change=format_stat_str(hours_change_percent, "1", True)
            )
        except Exception as e:
            self.logger.error(f"Error calculating monthly stats: {e}")
            raise ValidationException(detail="Failed to calculate monthly statistics")

    def get_formatted_recent_game(
            self,
            user_id: PyObjectId,
            game: GameDBOutput,
            table: Optional[TableDBOutput]
    ) -> RecentGameStats:
        """
        Format recent game statistics for display.
        
        Args:
            user_id: The ID of the user to get statistics for
            game: The game object containing game statistics
            table: Optional table object containing player information
            
        Returns:
            RecentGameStats: Formatted game statistics
            
        Raises:
            ValidationException: If game data is invalid or missing required fields
        """
        try:
            if not game or not hasattr(game, 'players'):
                raise ValidationException(detail="Invalid game data")

            player_count = len(
                [player for player in table.players if player.status == PlayerStatusEnum.CONFIRMED]
            ) if table and hasattr(table, 'players') else 0

            current_player = [player for player in game.players if player.user_id == user_id]
            if not current_player:
                raise ValidationException(detail="User not found in game players")

            player_data = current_player[0]
            return RecentGameStats(
                date=game.date.strftime("%b %d, %Y"),
                venue=game.venue,
                players=player_count,
                duration=f"{game.duration.hours}h {game.duration.minutes}m",
                profit_loss=player_data.net_profit,
                total_buy_in=sum([buyin.amount for buyin in player_data.buy_ins]),
                total_pot=game.total_pot,
                status=game.status,
            )
        except Exception as e:
            self.logger.error(f"Error formatting recent game stats: {e}")
            raise ValidationException(detail="Failed to format recent game statistics")
