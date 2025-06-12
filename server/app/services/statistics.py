from datetime import UTC, datetime, timedelta
from typing import List

from app.core.exceptions import DatabaseError
from app.schemas.statistics import DashboardStats, MonthlyChangesStats, RecentGameStats
from app.schemas.table import PlayerStatusEnum
from app.schemas.user import MonthlyStats, UserResponse, UserStats
from app.services.game import GameService
from app.services.table import TableService
from app.services.user import UserService


class StatisticsService:
    def __init__(
        self,
        user_service: UserService,
        game_service: GameService,
        table_service: TableService,
    ):
        self.user_service = user_service
        self.game_service = game_service
        self.table_service = table_service

    async def get_monthly_stats(self, user: UserResponse) -> List[MonthlyStats]:
        """Get monthly statistics for a user."""
        try:
            user_data = await self.user_service.get_user_by_id(user.id)
            if not user_data:
                return []

            return [MonthlyStats(**stats) for stats in user_data.monthly_stats]
        except Exception as e:
            raise DatabaseError(f"Failed to get monthly statistics: {str(e)}")

    async def get_dashboard_stats(self, user: UserResponse) -> DashboardStats:
        """Get dashboard statistics including current stats, monthly changes, and recent games."""
        try:
            # Get user data with stats
            user_data = await self.user_service.get_user_by_id(user.id)
            if not user_data:
                raise DatabaseError("User not found")

            # Get recent games
            recent_games = await self.game_service.get_recent_games(user.id, limit=5)

            # Format recent games
            formatted_games = []
            for game in recent_games:
                table = await self.table_service.get_table_by_id(str(game.table_id))
                player_count = (
                    len(
                        [
                            player
                            for player in table.players
                            if player.status == PlayerStatusEnum.CONFIRMED
                        ]
                    )
                    if table
                    else 0
                )

                current_player = [
                    player for player in game.players if player.user_id == user.id
                ]
                player_data = current_player[0] if current_player else {}

                formatted_games.append(
                    RecentGameStats(
                        date=game.date.strftime("%b %d, %Y"),
                        venue=game.venue,
                        players=player_count,
                        duration=f"{game.duration.hours}h {game.duration.minutes}m",
                        profit_loss=player_data.net_profit,
                        total_buy_in=sum(
                            [buyin.amount for buyin in player_data.buy_ins]
                        ),
                        total_pot=game.total_pot,
                        status=game.status,
                    )
                )

            # Calculate monthly changes
            monthly_changes = self._calculate_monthly_changes(user_data)

            return DashboardStats(
                user_stats=UserStats(
                    total_profit=user_data.stats.total_profit,
                    win_rate=user_data.stats.win_rate,
                    tables_played=user_data.stats.tables_played,
                    hours_played=user_data.stats.hours_played,
                ),
                monthly_changes=monthly_changes,
                recent_games=formatted_games,
            )

        except Exception as e:
            raise DatabaseError(f"Failed to get dashboard statistics: {str(e)}")

    def _calculate_monthly_changes(self, user: UserResponse) -> MonthlyChangesStats:
        """Calculate monthly changes in statistics."""
        current_month = datetime.now(UTC).strftime("%b %Y")
        previous_month = (
            datetime.utcnow().replace(day=1) - timedelta(days=1)
        ).strftime("%b %Y")

        current_month_stats = next(
            (stats for stats in user.monthly_stats if stats.month == current_month),
            MonthlyStats(month=current_month),
        )

        previous_month_stats = next(
            (stats for stats in user.monthly_stats if stats.month == previous_month),
            MonthlyStats(month=previous_month),
        )

        profit_change = current_month_stats.profit - previous_month_stats.profit
        win_rate_change = current_month_stats.win_rate - previous_month_stats.win_rate
        tables_change = (
            current_month_stats.tables_played - previous_month_stats.tables_played
        )
        hours_change = (
            current_month_stats.hours_played - previous_month_stats.hours_played
        )

        profit_change_percent = (
            (profit_change / previous_month_stats.profit) * 100
            if previous_month_stats.profit
            else 0
        )
        hours_change_percent = (
            (hours_change / previous_month_stats.hours_played) * 100
            if previous_month_stats.hours_played
            else 0
        )

        format_stat_str = lambda s: f"+{s:.0f}%" if s > 0 else f"{s:.0f}%"
        return MonthlyChangesStats(
            profit_change=format_stat_str(profit_change_percent),
            win_rate_change=format_stat_str(win_rate_change),
            tables_change=format_stat_str(tables_change),
            hours_change=format_stat_str(hours_change_percent),
        )
