from typing import List, Dict, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status, Body

from app.api.dependencies import get_current_user, get_game_service, get_table_service
from app.schemas.game import GameStatusEnum
from app.schemas.table import TableUpdate, TableBase, PlayerStatusEnum, TableDBOutput
from app.schemas.user import UserResponse
from app.services.game_service import GameService
from app.services.table_service import TableService

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=Optional[TableDBOutput])
async def create_table(table: TableBase,
                       current_user: UserResponse = Depends(get_current_user),
                       table_service: TableService = Depends(get_table_service)):
    try:
        table = await table_service.create_table(table, current_user)
        # await sse_handler.send_table_update(table_id=str(updated_table.id), data=updated_table)
        return table
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table creation failed: {e}"
        )


@router.get("/", response_model=List[TableDBOutput])
async def get_tables(
        status: str = None,
        limit: int = 10,
        skip: int = 0,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
):
    tables = await table_service.get_tables(current_user, status, skip, limit)
    return tables


@router.get("/{table_id}", response_model=TableDBOutput)
async def get_table(table_id: str, current_user: UserResponse = Depends(get_current_user),
                    table_service: TableService = Depends(get_table_service)):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    user_is_player = any(
        player.user_id == str(current_user.id)
        for player in table.players
    )
    if not user_is_player and table.creator_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return table


@router.put("/{table_id}", response_model=Optional[TableDBOutput])
async def update_table(
        table_id: str,
        table_update: TableUpdate,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")
    table = await table_service.get_by_id(table_id)

    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if str(table.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can modify the table")

    try:
        update_data = {k: v for k, v in table_update.model_dump(exclude_unset=True).items() if v is not None}
        updated_table = await table_service.update_table(table_id, update_data)
        # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
        return updated_table
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table update failed: {e}"
        )


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(table_id: str,
                       current_user: UserResponse = Depends(get_current_user),
                       table_service: TableService = Depends(get_table_service),
                       game_service: GameService = Depends(get_game_service)):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if str(table.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can delete the table")

    try:
        game_count = await game_service.count_games_for_table(table_id)
        updated_table = await table_service.delete_table(table_id, game_count)
        # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
        return updated_table
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table deletion failed: {e}"
        )


@router.put("/{table_id}/invite", status_code=status.HTTP_200_OK, response_model=Optional[TableDBOutput])
async def invite_user(
        table_id: str,
        friends: List[Dict] = Body(...),
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
):
    if not ObjectId.is_valid(table_id) or any(not ObjectId.is_valid(friend.get("user_id")) for friend in friends):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table or friends ID")

    updated_table = await table_service.invite_players(table_id, current_user, friends)
    # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
    return updated_table


@router.put("/{table_id}/{player_status}", status_code=status.HTTP_200_OK, response_model=Optional[TableDBOutput])
async def respond_to_invite(
        table_id: str,
        player_status: PlayerStatusEnum,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service),
        game_service: GameService = Depends(get_game_service)
):
    if not ObjectId.is_valid(table_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    player_obj = [player for player in table.players if player.user_id == str(current_user.id)]
    if not player_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant join table")

    updated_table = await table_service.respond_to_invite(table_id, str(current_user.id), player_status)

    if table.game_id and table.status == GameStatusEnum.IN_PROGRESS:
        await game_service.update_game_invite(table.game_id, current_user, player_status)

    # await sse_handler.send_table_update(table_id=table_id, data=updated_table)
    return updated_table
