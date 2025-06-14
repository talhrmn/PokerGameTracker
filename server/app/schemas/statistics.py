from datetime import datetime, UTC
from typing import List

from pydantic import BaseModel, Field, computed_field

from app.schemas.game import GameStatusEnum
from app.schemas.py_object_id import PyObjectId


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


class Stats(BaseModel):
    total_profit: float = 0
    games_won: int = 0
    games_lost: int = 0
    tables_played: int = 0
    hours_played: float = 0

    @computed_field
    @property
    def win_rate(self) -> float:
        total_games = self.games_won + self.games_lost
        return self.games_won / total_games if total_games > 0 else 0


class DashboardStats(BaseModel):
    user_stats: Stats
    monthly_changes: MonthlyChangesStats
    recent_games: List[RecentGameStats]


class MonthlyStats(BaseModel):
    month: str
    profit: float = 0
    games_won: int = 0
    games_lost: int = 0
    tables_played: int = 0
    hours_played: float = 0

    @computed_field
    @property
    def win_rate(self) -> float:
        total_games = self.games_won + self.games_lost
        return self.games_won / total_games if total_games > 0 else 0


class StatisticsBase(BaseModel):
    user_id: PyObjectId
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stats: Stats = Field(default_factory=Stats)
    monthly_stats: List[MonthlyStats] = []


class StatisticsDBOutput(StatisticsBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
        "extra": "ignore"
    }
