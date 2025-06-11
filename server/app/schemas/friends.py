from typing import List

from pydantic import BaseModel

from app.schemas.user import UserResponse


class FriendsResponse(BaseModel):
    friends: List[UserResponse]
    friends_invited: List[UserResponse]
    friend_invites: List[UserResponse]
