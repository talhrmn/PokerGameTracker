from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_user_service, get_friends_service
from app.core.exceptions import ValidationException
from app.schemas.friends import FriendsResponse
from app.schemas.user import UserResponse
from app.services.friends_service import FriendsService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=FriendsResponse)
async def get_friends(
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
        friends_service: FriendsService = Depends(get_friends_service)
) -> FriendsResponse:
    """
    Get categorized list of friends.
    
    Args:
        current_user: The current authenticated user
        user_service: The user service
        friends_service: The friends service
        
    Returns:
        Categorized list of friends
    """
    friends = await user_service.get_user_friends(str(current_user.id))
    invited_friends = await user_service.get_user_invited_friends(str(current_user.id))
    return friends_service.categorize_friends(friends, invited_friends)


@router.post("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_friend(
        friend_id: str,
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> None:
    """
    Add a friend.
    
    Args:
        friend_id: ID of the user to add as friend
        current_user: The current authenticated user
        user_service: The user service
    """
    user_id = ObjectId(current_user.id)
    friend_obj_id = ObjectId(friend_id)

    if str(user_id) == friend_id:
        raise ValidationException(detail="Cannot add yourself as a friend")

    await user_service.add_friend(str(user_id), str(friend_obj_id))


@router.delete("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
        friend_id: str,
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> None:
    """
    Remove a friend.
    
    Args:
        friend_id: ID of the friend to remove
        current_user: The current authenticated user
        user_service: The user service
    """
    user_id = ObjectId(current_user.id)
    friend_obj_id = ObjectId(friend_id)
    await user_service.remove_friend(str(user_id), str(friend_obj_id))


@router.get("/search/{friend_regex}", response_model=List[UserResponse])
async def search_users(
        friend_regex: str,
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """
    Search for users.
    
    Args:
        friend_regex: Search pattern for usernames
        current_user: The current authenticated user
        user_service: The user service
        
    Returns:
        List of matching users
    """
    user_id = ObjectId(current_user.id)
    users = await user_service.search_users(str(user_id), friend_regex)
    return [UserResponse(**user.model_dump()) for user in users]
