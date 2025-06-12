from typing import List

from app.api.dependencies import get_current_user, get_user_service
from app.core.exceptions import DatabaseError, InvalidInputError, ResourceNotFoundError
from app.schemas.friends import FriendsResponse
from app.schemas.user import UserResponse
from app.services.user import UserService
from bson import ObjectId
from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.get("/", response_model=FriendsResponse)
async def get_friends(
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> FriendsResponse:
    """Get all friends for the current user."""
    try:
        friends = await user_service.get_user_friends(current_user.id)
        friends_invited_docs = await user_service.get_user_invited_friends(
            current_user.id
        )

        user_friends_response = [
            UserResponse(user_id=str(friend.get("_id")), **friend) for friend in friends
        ]
        friends_invited_objs = [
            UserResponse(user_id=str(friend.get("_id")), **friend)
            for friend in friends_invited_docs
        ]

        friends_response = [
            friend for friend in user_friends_response if friend in friends_invited_objs
        ]
        friends_invited_response = [
            friend
            for friend in user_friends_response
            if friend not in friends_invited_objs
        ]
        friend_invites_response = [
            friend
            for friend in friends_invited_objs
            if friend not in user_friends_response
        ]

        return FriendsResponse(
            friends=friends_response,
            friends_invited=friends_invited_response,
            friend_invites=friend_invites_response,
        )
    except Exception as e:
        raise DatabaseError(f"Failed to get friends: {str(e)}")


@router.post("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_friend(
    friend_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    if not ObjectId.is_valid(friend_id):
        raise InvalidInputError("Invalid friend ID format")

    if str(current_user.id) == friend_id:
        raise InvalidInputError("Cannot add yourself as a friend")

    try:
        friend = await user_service.get_user_by_id(friend_id)
        if not friend:
            raise ResourceNotFoundError("User not found")

        await user_service.update_friends(
            user_id=ObjectId(current_user.id), friend_id=ObjectId(friend_id)
        )
    except ResourceNotFoundError as e:
        raise e
    except Exception as e:
        raise DatabaseError(f"Failed to add friend: {str(e)}")


@router.delete("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    friend_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    if not ObjectId.is_valid(friend_id):
        raise InvalidInputError("Invalid friend ID format")

    try:
        await user_service.remove_friends(
            user_id=ObjectId(current_user.id), friend_id=ObjectId(friend_id)
        )
    except Exception as e:
        raise DatabaseError(f"Failed to remove friend: {str(e)}")


@router.get("/search/{friend_regex}", response_model=List[UserResponse])
async def search_users(
    friend_regex: str,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Search for users by regex pattern."""
    if not friend_regex or len(friend_regex) < 2:
        raise InvalidInputError("Search query must be at least 2 characters long")

    try:
        users = await user_service.search_user(
            user_id=ObjectId(current_user.id), friend_regex=friend_regex
        )
        return [UserResponse(**user) for user in users]
    except Exception as e:
        raise DatabaseError(f"Failed to search users: {str(e)}")
