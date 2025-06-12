from datetime import datetime, UTC
from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.py_object_id import PyObjectId


class GameStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CashOut(BaseModel):
    amount: float
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BuyIn(BaseModel):
    amount: float
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NotableHand(BaseModel):
    hand_id: str
    description: str
    amount_won: float


class GamePlayer(BaseModel):
    user_id: PyObjectId
    username: str
    buy_ins: List[BuyIn] = []
    cash_out: float = 0
    net_profit: float = 0
    notable_hands: List[NotableHand] = []


class Duration(BaseModel):
    hours: int = 0
    minutes: int = 0


class GameBase(BaseModel):
    table_id: PyObjectId
    date: datetime
    venue: str
    players: List[GamePlayer]
    status: GameStatusEnum = GameStatusEnum.IN_PROGRESS


class GameUpdate(BaseModel):
    venue: Optional[str] = None
    duration: Optional[Duration] = None
    players: Optional[List[GamePlayer]] = None
    total_pot: Optional[float] = None
    status: Optional[GameStatusEnum] = None


class GameDBInput(GameBase):
    duration: Duration = Duration()
    creator_id: str
    total_pot: float = 0
    available_cash_out: float = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GameDBOutput(GameDBInput):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
