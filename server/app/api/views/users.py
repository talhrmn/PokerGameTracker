from fastapi import APIRouter, HTTPException, Depends, status

from app.api.dependencies import get_current_user, get_user_service
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me")
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.put("/me")
async def update_user_profile(
        user_update: UserUpdate,
        current_user: UserResponse = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
):
    update_data = {k: v for k, v in user_update.model_dump(exclude_unset=True).items() if v is not None}
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    try:
        await user_service.update_user_data(str(current_user.id), update_data)
        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User update failed: {e}"
        )
