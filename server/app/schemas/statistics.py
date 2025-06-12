from typing import List

from app.schemas.game import GameStatusEnum
from app.schemas.user import UserStats
from pydantic import BaseModel


class MonthlyChangesStats(BaseModel):
    profit_change: str
    win_rate_change: str
    tables_change: str
    hours_change: str


class RecentGameStats(BaseModel):
    date: str
    venue: str
    players: int
    duration: str
    profit_loss: float
    total_pot: float
    total_buy_in: float
    status: GameStatusEnum


class DashboardStats(BaseModel):
    user_stats: UserStats
    monthly_changes: MonthlyChangesStats
    recent_games: List[RecentGameStats]
