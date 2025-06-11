from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.dependencies import get_current_user, get_database
from app.handlers.dash_stats import dash_stats_handler
from app.handlers.games import game_handler
from app.handlers.tables import table_handler
from app.handlers.users import user_handler
from app.schemas.dash_stats import DashboardStats, RecentGameStats
from app.schemas.table import PlayerStatusEnum
from app.schemas.user import UserResponse, UserStats

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_user: UserResponse = Depends(get_current_user),
                              db_client: AsyncIOMotorClient = Depends(get_database)):
    user = await user_handler.get_user_by_id(user_id=current_user.id, db_client=db_client)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recent_games = await game_handler.get_recent_games(user_id=current_user.id, limit=5, db_client=db_client)

    formatted_games = []
    for game in recent_games:
        table = await table_handler.get_table_by_id(table_id=str(game.table_id), db_client=db_client)
        player_count = len(
            [player for player in table.players if player.status == PlayerStatusEnum.CONFIRMED]) if table else 0

        current_player = [player for player in game.players if player.user_id == current_user.id]
        player_data = current_player[0] if current_player else {}

        formatted_games.append(RecentGameStats(
            date=game.date.strftime("%b %d, %Y"),
            venue=game.venue,
            players=player_count,
            duration=f"{game.duration.hours}h {game.duration.minutes}m",
            profit_loss=player_data.net_profit,
            total_buy_in=sum([buyin.amount for buyin in player_data.buy_ins]),
            total_pot=game.total_pot,
            status=game.status,
        ))

    user_monthly_changes = dash_stats_handler.get_user_monthly_change_stats(user=user)

    dashboard_data = DashboardStats(
        user_stats=UserStats(
            total_profit=user.stats.total_profit,
            win_rate=user.stats.win_rate,
            tables_played=user.stats.tables_played,
            hours_played=user.stats.hours_played
        ),
        monthly_changes=user_monthly_changes,
        recent_games=formatted_games
    )

    return dashboard_data
