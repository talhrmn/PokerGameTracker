from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status

from app.api.dependencies import get_current_user, get_user_service, get_friends_service
from app.schemas.friends import FriendsResponse
from app.schemas.user import UserResponse
from app.services.friends_service import FriendsService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=FriendsResponse)
async def get_friends(current_user: UserResponse = Depends(get_current_user),
                      user_service: UserService = Depends(get_user_service),
                      friends_service: FriendsService = Depends(get_friends_service)) -> FriendsResponse:
    friends = await user_service.get_user_friends(str(current_user.id))
    invited_friends = await user_service.get_user_invited_friends(str(current_user.id))
    return friends_service.categorize_friends(friends, invited_friends)


@router.post("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_friend(friend_id: str,
                     current_user: UserResponse = Depends(get_current_user),
                     user_service: UserService = Depends(get_user_service)) -> None:
    user_id = ObjectId(current_user.id)
    if not ObjectId.is_valid(friend_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    friend_obj_id = ObjectId(friend_id)
    friend = await user_service.get_by_id(friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user_id) == friend_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")
    await user_service.add_friend(str(user_id), str(friend_obj_id))


@router.delete("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(friend_id: str,
                        current_user: UserResponse = Depends(get_current_user),
                        user_service: UserService = Depends(get_user_service)) -> None:
    user_id = ObjectId(current_user.id)
    if not ObjectId.is_valid(friend_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    friend_obj_id = ObjectId(friend_id)
    await user_service.remove_friend(str(user_id), str(friend_obj_id))


@router.get("/search/{friend_regex}", response_model=List[UserResponse])
async def search_users(
        friend_regex: str,
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)):
    user_id = ObjectId(current_user.id)
    users = await user_service.search_users(str(user_id), friend_regex)
    return [UserResponse(**user.model_dump()) for user in users]
