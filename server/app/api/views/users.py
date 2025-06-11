from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient

from server.app.api.dependencies import get_current_user, get_database
from server.app.core.security import get_password_hash
from server.app.handlers.users import user_handler
from server.app.schemas.user import UserUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.put("/me")
async def update_user_profile(
        user_update: UserUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    user_id = ObjectId(current_user.id)
    update_data = {k: v for k, v in user_update.model_dump(exclude_unset=True).items() if v is not None}
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    try:
        user_handler.update_user_data(user_id=user_id, update_data=update_data, db_client=db_client)
        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User update failed: {e}"
        )
