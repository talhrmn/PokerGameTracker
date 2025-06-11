from typing import Dict

from pydantic import BaseModel


class TrendsResponse(BaseModel):
    average_pot_size: float
    average_win_rate: float
    average_hours_played: float
    average_num_of_players: float
    pot_trend: Dict[str, int]
    players_trend: Dict[str, int]
    duration_trend: Dict[str, float]
    profit_trend: Dict[str, Dict[str, int]]
    buy_in_trend: Dict[str, Dict[str, int]]
