import logging
from datetime import datetime, UTC, timedelta
from typing import Optional

from app.core.exceptions import ValidationException
from app.schemas.dash_stats import MonthlyChangesStats, RecentGameStats
from app.schemas.game import GameDBOutput
from app.schemas.py_object_id import PyObjectId
from app.schemas.table import TableDBOutput, PlayerStatusEnum
from app.schemas.user import MonthlyStats, UserDBOutput


class StatisticsService:
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

    def __init__(self):
        """Initialize the statistics service with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_user_monthly_change_stats(self, user: UserDBOutput) -> MonthlyChangesStats:
        """
        Calculate monthly statistics changes for a user.
        
        Args:
            user: The user object containing monthly statistics
            
        Returns:
            MonthlyChangesStats: Object containing formatted percentage changes
            
        Raises:
            ValidationException: If user data is invalid or missing required fields
        """
        try:
            if not user or not hasattr(user, 'monthly_stats'):
                raise ValidationException(detail="Invalid user data")

            current_month = datetime.now(UTC).strftime("%b %Y")
            previous_month = (datetime.now(UTC).replace(day=1) - timedelta(days=1)).strftime("%b %Y")

            current_month_stats = next(
                (stats for stats in user.monthly_stats if stats.month == current_month),
                MonthlyStats(month=current_month)
            )

            previous_month_stats = next(
                (stats for stats in user.monthly_stats if stats.month == previous_month),
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

            format_stat_str = lambda s: f"+{s:.0f}%" if s > 0 else f"{s:.0f}%"
            return MonthlyChangesStats(
                profit_change=format_stat_str(profit_change_percent),
                win_rate_change=format_stat_str(win_rate_change),
                tables_change=format_stat_str(tables_change),
                hours_change=format_stat_str(hours_change_percent)
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
