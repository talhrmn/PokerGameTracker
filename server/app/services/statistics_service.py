from datetime import datetime, UTC, timedelta

from app.schemas.dash_stats import MonthlyChangesStats, RecentGameStats
from app.schemas.game import GameDBOutput
from app.schemas.py_object_id import PyObjectId
from app.schemas.table import TableDBOutput, PlayerStatusEnum
from app.schemas.user import MonthlyStats, UserDBOutput


class StatisticsService:

    def __init__(self):
        pass

    def get_user_monthly_change_stats(self, user: UserDBOutput) -> MonthlyChangesStats:
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

    def get_formatted_recent_game(self, user_id: PyObjectId, game: GameDBOutput, table: TableDBOutput):
        player_count = len(
            [player for player in table.players if player.status == PlayerStatusEnum.CONFIRMED]) if table else 0
        current_player = [player for player in game.players if player.user_id == user_id]
        player_data = current_player[0] if current_player else {}
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
