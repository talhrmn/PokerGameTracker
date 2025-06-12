from typing import List

from app.schemas.user import UserResponse
from pydantic import BaseModel


class FriendsResponse(BaseModel):
    friends: List[UserResponse]
    friends_invited: List[UserResponse]
    friend_invites: List[UserResponse]
