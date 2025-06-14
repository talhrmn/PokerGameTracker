from datetime import datetime, UTC
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.game import GameStatusEnum
from app.schemas.py_object_id import PyObjectId


class PlayerStatusEnum(str, Enum):
    INVITED = "invited"
    CONFIRMED = "confirmed"
    DECLINED = "declined"


class PlayerStatus(BaseModel):
    user_id: PyObjectId
    username: str
    status: PlayerStatusEnum


class TableBase(BaseModel):
    name: str
    date: datetime
    minimum_buy_in: float
    maximum_players: int
    game_type: str
    blind_structure: str
    description: Optional[str] = None
    venue: str


class TableUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[datetime] = None
    minimum_buy_in: Optional[float] = None
    maximum_players: Optional[int] = None
    game_type: Optional[str] = None
    blind_structure: Optional[str] = None
    description: Optional[str] = None
    venue: Optional[str] = None
    status: Optional[GameStatusEnum] = None


class PlayerStatusResponse(BaseModel):
    user_id: str
    username: str
    status: PlayerStatusEnum


class TableResponse(BaseModel):
    id: str
    name: str
    date: str
    game_type: str
    venue: str
    players: List[PlayerStatusResponse]
    minimum_buy_in: int
    maximum_players: int
    status: GameStatusEnum
    creator_id: str

    class Config:
        from_attributes = True


class TableDBInput(TableBase):
    game_id: Optional[str] = None
    creator_id: PyObjectId
    status: GameStatusEnum = GameStatusEnum.SCHEDULED
    players: List[PlayerStatus] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TableDBOutput(TableDBInput):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str}
    }


class TableCountResponse(BaseModel):
    tables: List[TableDBOutput]
    count: int
