from app.api.dependencies import get_current_user, get_user_service
from app.core.exceptions import DatabaseError, InvalidInputError
from app.core.security import get_password_hash
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService
from bson import ObjectId
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user),
):
    """Get the current user's profile."""
    return current_user


@router.put("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update the current user's profile."""
    user_id = ObjectId(current_user.id)
    update_data = {
        k: v
        for k, v in user_update.model_dump(exclude_unset=True).items()
        if v is not None
    }

    if not update_data:
        raise InvalidInputError("No update data provided")

    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    try:
        await user_service.update_user_data(user_id=user_id, update_data=update_data)
    except Exception as e:
        raise DatabaseError(f"User update failed: {str(e)}")


@router.get("/friends")
async def get_user_friends(
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get the current user's friends."""
    try:
        return await user_service.get_user_friends(current_user.id)
    except Exception as e:
        raise DatabaseError(f"Failed to get friends: {str(e)}")


@router.get("/invited-friends")
async def get_user_invited_friends(
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get the current user's invited friends."""
    try:
        return await user_service.get_user_invited_friends(current_user.id)
    except Exception as e:
        raise DatabaseError(f"Failed to get invited friends: {str(e)}")


@router.post("/friends/{friend_id}")
async def add_friend(
    friend_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    if not ObjectId.is_valid(friend_id):
        raise InvalidInputError("Invalid friend ID format")

    try:
        await user_service.update_friends(
            user_id=ObjectId(current_user.id), friend_id=ObjectId(friend_id)
        )
    except Exception as e:
        raise DatabaseError(f"Failed to add friend: {str(e)}")


@router.delete("/friends/{friend_id}")
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


@router.get("/search")
async def search_users(
    query: str,
    current_user: UserResponse = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Search for users."""
    if not query or len(query) < 2:
        raise InvalidInputError("Search query must be at least 2 characters long")

    try:
        return await user_service.search_user(
            user_id=ObjectId(current_user.id), friend_regex=query
        )
    except Exception as e:
        raise DatabaseError(f"Failed to search users: {str(e)}")
