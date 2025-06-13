from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_user_service
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate, UserResponse, UserDBOutput
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get the current user's profile.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The current user's profile
    """
    return current_user


@router.put("/me", response_model=UserDBOutput)
async def update_user_profile(
        user_update: UserUpdate,
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
) -> UserDBOutput:
    """
    Update the current user's profile.
    
    Args:
        user_update: The user data to update
        current_user: The current authenticated user
        user_service: The user service
        
    Returns:
        The updated user
    """
    update_data = {k: v for k, v in user_update.model_dump(exclude_unset=True).items() if v is not None}
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    return await user_service.update_user_data(str(current_user.id), update_data)
