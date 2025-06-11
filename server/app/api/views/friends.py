from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.dependencies import get_current_user, get_database
from app.handlers.users import user_handler
from app.schemas.friends import FriendsResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/", response_model=FriendsResponse)
async def get_friends(current_user: UserResponse = Depends(get_current_user),
                      db_client: AsyncIOMotorClient = Depends(get_database)) -> FriendsResponse:
    friends = await user_handler.get_user_friends(user_id=current_user.id, db_client=db_client)

    user_friends_response = [UserResponse(user_id=str(friend.get("_id")), **friend) for friend in friends]
    friends_invited_docs = await user_handler.get_user_invited_friends(user_id=current_user.id, db_client=db_client)
    friends_invited_objs = [UserResponse(user_id=str(friend.get("_id")), **friend) for friend in friends_invited_docs]

    friends_response = [friend for friend in user_friends_response if friend in friends_invited_objs]
    friends_invited_response = [friend for friend in user_friends_response if friend not in friends_invited_objs]
    friend_invites_response = [friend for friend in friends_invited_objs if friend not in user_friends_response]

    return FriendsResponse(
        friends=friends_response,
        friends_invited=friends_invited_response,
        friend_invites=friend_invites_response
    )


@router.post("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_friend(friend_id: str, current_user: UserResponse = Depends(get_current_user),
                     db_client: AsyncIOMotorClient = Depends(get_database)):
    user_id = ObjectId(current_user.id)
    if not ObjectId.is_valid(friend_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    friend_obj_id = ObjectId(friend_id)
    friend = await user_handler.get_user_by_id(friend_id, db_client=db_client)
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user_id) == friend_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")
    await user_handler.update_friends(user_id=user_id, friend_id=friend_obj_id, db_client=db_client)


@router.delete("/friends/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(friend_id: str, current_user: UserResponse = Depends(get_current_user),
                        db_client: AsyncIOMotorClient = Depends(get_database)):
    user_id = ObjectId(current_user.id)
    if not ObjectId.is_valid(friend_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    friend_obj_id = ObjectId(friend_id)
    await user_handler.remove_friends(user_id=user_id, friend_id=friend_obj_id, db_client=db_client)


@router.get("/search/{friend_regex}", response_model=List[UserResponse])
async def search_users(
        friend_regex: str,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    user_id = ObjectId(current_user.id)
    users = await user_handler.search_user(user_id=user_id, friend_regex=friend_regex, db_client=db_client)
    return [UserResponse(**user) for user in users]
