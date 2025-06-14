from typing import List, Dict, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, status, Body

from app.api.dependencies import get_current_user, get_game_service, get_table_service
from app.core.exceptions import ValidationException, NotFoundException, PermissionDeniedException
from app.schemas.game import GameStatusEnum
from app.schemas.table import TableUpdate, TableBase, PlayerStatusEnum, TableDBOutput, TableCountResponse
from app.schemas.user import UserResponse
from app.services.game_service import GameService
from app.services.table_service import TableService

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=Optional[TableDBOutput])
async def create_table(
        table: TableBase,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
) -> TableDBOutput:
    """
    Create a new table.
    
    Args:
        table: Table data
        current_user: The current authenticated user
        table_service: The table service
        
    Returns:
        The created table
    """
    return await table_service.create_table(table, current_user)


@router.get("/", response_model=List[TableDBOutput])
async def get_tables(
        status: str = None,
        limit: int = 10,
        skip: int = 0,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
) -> List[TableDBOutput]:
    """
    Get tables for the current user.
    
    Args:
        status: Optional status to filter by
        limit: Optional limit for pagination
        skip: Optional skip for pagination
        current_user: The current authenticated user
        table_service: The table service
        
    Returns:
        List of tables
    """
    return await table_service.get_tables(current_user, status, skip, limit)


@router.get("/created", response_model=TableCountResponse)
async def get_created_tables(
        status: str = None,
        limit: int = 10,
        skip: int = 0,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)):
    """
    Get created tables for the current user.

    Args:
        status: Optional status to filter by
        limit: Optional limit for pagination
        skip: Optional skip for pagination
        current_user: The current authenticated user
        table_service: The table service

    Returns:
        List of tables
    """
    return await table_service.get_created_tables(current_user, status, skip, limit)


@router.get("/invited", response_model=TableCountResponse)
async def get_invited_tables(
        status: str = None,
        limit: int = 10,
        skip: int = 0,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
):
    """
    Get invited tables for the current user.

    Args:
        status: Optional status to filter by
        limit: Optional limit for pagination
        skip: Optional skip for pagination
        current_user: The current authenticated user
        table_service: The table service

    Returns:
        List of tables
    """
    return await table_service.get_invited_tables(current_user, status, skip, limit)

@router.get("/{table_id}", response_model=TableDBOutput)
async def get_table(
        table_id: str,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
) -> TableDBOutput:
    """
    Get a specific table.
    
    Args:
        table_id: ID of the table
        current_user: The current authenticated user
        table_service: The table service
        
    Returns:
        The table data
    """
    if not ObjectId.is_valid(table_id):
        raise ValidationException(detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise NotFoundException(detail="Table not found")

    user_is_player = any(player.user_id == str(current_user.id) for player in table.players)
    if not user_is_player and table.creator_id != str(current_user.id):
        raise PermissionDeniedException(detail="Access denied")

    return table


@router.put("/{table_id}", response_model=Optional[TableDBOutput])
async def update_table(
        table_id: str,
        table_update: TableUpdate,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
) -> TableDBOutput:
    """
    Update a table.
    
    Args:
        table_id: ID of the table
        table_update: Updated table data
        current_user: The current authenticated user
        table_service: The table service
        
    Returns:
        The updated table
    """
    if not ObjectId.is_valid(table_id):
        raise ValidationException(detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise NotFoundException(detail="Table not found")

    if str(table.creator_id) != str(current_user.id):
        raise PermissionDeniedException(detail="Only the creator can modify the table")

    update_data = {k: v for k, v in table_update.model_dump(exclude_unset=True).items() if v is not None}
    return await table_service.update_table(table_id, update_data)


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
        table_id: str,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service),
        game_service: GameService = Depends(get_game_service)
) -> None:
    """
    Delete a table.
    
    Args:
        table_id: ID of the table
        current_user: The current authenticated user
        table_service: The table service
        game_service: The game service
    """
    if not ObjectId.is_valid(table_id):
        raise ValidationException(detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise NotFoundException(detail="Table not found")

    if str(table.creator_id) != str(current_user.id):
        raise PermissionDeniedException(detail="Only the creator can delete the table")

    game_count = await game_service.count_games_for_table(table_id)
    return await table_service.delete_table(table_id, game_count)


@router.put("/{table_id}/invite", status_code=status.HTTP_200_OK, response_model=Optional[TableDBOutput])
async def invite_user(
        table_id: str,
        friends: List[Dict] = Body(...),
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service)
) -> TableDBOutput:
    """
    Invite users to a table.
    
    Args:
        table_id: ID of the table
        friends: List of friends to invite
        current_user: The current authenticated user
        table_service: The table service
        
    Returns:
        The updated table
    """
    if not ObjectId.is_valid(table_id) or any(not ObjectId.is_valid(friend.get("user_id")) for friend in friends):
        raise ValidationException(detail="Invalid table or friends ID")

    return await table_service.invite_players(table_id, current_user, friends)


@router.put("/{table_id}/{player_status}", status_code=status.HTTP_200_OK, response_model=Optional[TableDBOutput])
async def respond_to_invite(
        table_id: str,
        player_status: PlayerStatusEnum,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service),
        game_service: GameService = Depends(get_game_service)
) -> TableDBOutput:
    """
    Respond to a table invite.
    
    Args:
        table_id: ID of the table
        player_status: The player's response status
        current_user: The current authenticated user
        table_service: The table service
        game_service: The game service
        
    Returns:
        The updated table
    """
    if not ObjectId.is_valid(table_id):
        raise ValidationException(detail="Invalid table ID")

    table = await table_service.get_by_id(table_id)
    if not table:
        raise NotFoundException(detail="Table not found")

    player_obj = [player for player in table.players if player.user_id == str(current_user.id)]
    if not player_obj:
        raise ValidationException(detail="Cannot join table")

    updated_table = await table_service.respond_to_invite(table_id, str(current_user.id), player_status)

    if table.game_id and table.status == GameStatusEnum.IN_PROGRESS:
        await game_service.update_game_invite(table.game_id, current_user, player_status)

    return updated_table
