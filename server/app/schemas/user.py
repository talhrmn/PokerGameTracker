from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr

from server.app.schemas.py_object_id import PyObjectId


class UserStats(BaseModel):
    total_profit: float = 0
    win_rate: float = 0
    tables_played: int = 0
    hours_played: float = 0


class MonthlyStats(BaseModel):
    month: str
    profit: float = 0
    win_rate: float = 0
    tables_played: int = 0
    hours_played: float = 0


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserResponse(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_pic: Optional[str] = None


class UserDBInput(UserBase):
    password_hash: str
    profile_pic: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    stats: UserStats = Field(default_factory=UserStats)
    monthly_stats: List[MonthlyStats] = []
    friends: List[PyObjectId] = []


class UserDBResponse(UserDBInput):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str}
    }
