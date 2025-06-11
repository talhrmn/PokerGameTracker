from typing import List, Dict, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status, Body
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.dependencies import get_current_user, get_database
from app.handlers.games import game_handler
from app.handlers.sse import sse_handler
from app.handlers.tables import table_handler
from app.schemas.game import GameStatusEnum
from app.schemas.table import TableUpdate, TableBase, PlayerStatusEnum, TableDBResponse, PlayerStatus
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=Optional[TableDBResponse])
async def create_table(table: TableBase, current_user: UserResponse = Depends(get_current_user),
                       db_client: AsyncIOMotorClient = Depends(get_database)):
    try:
        table_id = await table_handler.create_table(table=table, current_user=current_user, db_client=db_client)
        updated_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
        # await sse_handler.send_table_update(table_id=str(updated_table.id), data=updated_table)
        return updated_table
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table creation failed: {e}"
        )


@router.get("/", response_model=List[TableDBResponse])
async def get_tables(
        status: str = None,
        limit: int = 10,
        skip: int = 0,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    tables = await table_handler.get_tables(status=status, limit=limit, skip=skip, current_user=current_user,
                                            db_client=db_client)
    return tables


@router.get("/{table_id}", response_model=TableDBResponse)
async def get_table(table_id: str, current_user: UserResponse = Depends(get_current_user),
                    db_client: AsyncIOMotorClient = Depends(get_database)):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")

    table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    user_is_player = any(
        player.user_id == str(current_user.id)
        for player in table.players
    )
    if not user_is_player and table.creator_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return table


@router.put("/{table_id}", response_model=Optional[TableDBResponse])
async def update_table(
        table_id: str,
        table_update: TableUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")
    existing_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)

    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if str(existing_table.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can modify the table")

    try:
        update_data = {k: v for k, v in table_update.model_dump(exclude_unset=True).items() if v is not None}
        await table_handler.update_table(table_id=table_id, update_data=update_data, db_client=db_client)

        updated_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
        # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
        return updated_table
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table update failed: {e}"
        )


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(table_id: str, current_user: UserResponse = Depends(get_current_user),
                       db_client: AsyncIOMotorClient = Depends(get_database)):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")
    existing_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)

    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if str(existing_table.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can delete the table")
    try:
        await table_handler.delete_table(table_id=table_id, db_client=db_client)
        updated_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
        # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
        return updated_table
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table deletion failed: {e}"
        )


@router.put("/{table_id}/invite", status_code=status.HTTP_200_OK, response_model=Optional[TableDBResponse])
async def invite_user(
        table_id: str,
        friends: List[Dict] = Body(...),
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    if not ObjectId.is_valid(table_id) or any(not ObjectId.is_valid(friend.get("user_id")) for friend in friends):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table or friends ID")
    existing_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)

    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if not existing_table.creator_id == str(current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant invite to table")

    table_player_ids = {player.user_id for player in existing_table.players}
    table_players = [player.model_dump() for player in existing_table.players]
    for friend in friends:
        friend_id = friend["user_id"]
        if friend_id not in table_player_ids:
            table_players.append(PlayerStatus(user_id=friend_id, username=friend["username"],
                                              status=PlayerStatusEnum.INVITED.value).model_dump())
    update_data = {"players": table_players}
    await table_handler.update_table(table_id=table_id, update_data=update_data, db_client=db_client)
    updated_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
    # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
    return updated_table


@router.put("/{table_id}/{player_status}", status_code=status.HTTP_200_OK, response_model=Optional[TableDBResponse])
async def respond_to_invite(
        table_id: str,
        player_status: PlayerStatusEnum,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")

    existing_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
    if not existing_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    player_obj = [player for player in existing_table.players if player.user_id == str(current_user.id)]
    if not player_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant join table")

    await table_handler.respond_to_invite_table(table_id=table_id, player_id=str(current_user.id),
                                                status=player_status, db_client=db_client)

    if existing_table.game_id and existing_table.status == GameStatusEnum.IN_PROGRESS:
        await game_handler.update_game_invite(game_id=existing_table.game_id, user=current_user, status=player_status,
                                              db_client=db_client)

    updated_table = await table_handler.get_table_by_id(table_id=table_id, db_client=db_client)
    # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
    return updated_table
