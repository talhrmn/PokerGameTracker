from typing import List, Optional

from app.api.dependencies import (
    get_current_user,
    get_table_service,
)
from app.core.exceptions import DatabaseError, InvalidInputError, ResourceNotFoundError
from app.schemas.table import (
    PlayerStatusEnum,
    TableCreate,
    TableDBResponse,
    TableUpdate,
)
from app.schemas.user import UserResponse
from app.services.table import TableService
from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post("/", response_model=TableDBResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
    table_data: TableCreate,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Create a new table."""
    try:
        return await table_service.create_table(table_data, current_user)
    except Exception as e:
        raise DatabaseError(f"Failed to create table: {str(e)}")


@router.get("/", response_model=List[TableDBResponse])
async def get_tables(
    status: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Get all tables for the current user."""
    try:
        return await table_service.get_tables(status, limit, skip)
    except Exception as e:
        raise DatabaseError(f"Failed to get tables: {str(e)}")


@router.get("/{table_id}", response_model=TableDBResponse)
async def get_table(
    table_id: str,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Get a specific table."""
    try:
        table = await table_service.get_table_by_id(table_id)
        if not table:
            raise ResourceNotFoundError(f"Table {table_id} not found")

        # Check if user is a player or creator
        if (
            str(current_user.id) not in [p.user_id for p in table.players]
            and str(current_user.id) != table.creator_id
        ):
            raise InvalidInputError("You don't have access to this table")

        return table
    except Exception as e:
        raise DatabaseError(f"Failed to get table: {str(e)}")


@router.put("/{table_id}", response_model=TableDBResponse)
async def update_table(
    table_id: str,
    table_data: TableUpdate,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Update a table."""
    try:
        table = await table_service.get_table_by_id(table_id)
        if not table:
            raise ResourceNotFoundError("Table not found")

        # Check if user is the creator
        if table.creator_id != str(current_user.id):
            raise InvalidInputError("Only the creator can modify the table")

        return await table_service.update_table(
            table_id, table_data.dict(exclude_unset=True)
        )
    except Exception as e:
        raise DatabaseError(f"Failed to update table: {str(e)}")


@router.post("/{table_id}/invite/{user_id}", response_model=TableDBResponse)
async def invite_player(
    table_id: str,
    user_id: str,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Invite a player to the table."""
    try:
        table = await table_service.get_table_by_id(table_id)
        if not table:
            raise ResourceNotFoundError("Table not found")

        # Check if user is the creator
        if table.creator_id != str(current_user.id):
            raise InvalidInputError("Only the creator can invite players")

        return await table_service.invite_player(table_id, user_id)
    except Exception as e:
        raise DatabaseError(f"Failed to invite player: {str(e)}")


@router.put("/{table_id}/respond", response_model=TableDBResponse)
async def respond_to_invite(
    table_id: str,
    status: PlayerStatusEnum,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Respond to a table invite."""
    try:
        table = await table_service.get_table_by_id(table_id)
        if not table:
            raise ResourceNotFoundError("Table not found")

        # Check if user is invited
        user_is_invited = any(
            player.user_id == str(current_user.id)
            and player.status == PlayerStatusEnum.INVITED
            for player in table.players
        )
        if not user_is_invited:
            raise InvalidInputError("You are not invited to this table")

        return await table_service.respond_to_invite_table(
            table_id, str(current_user.id), status
        )
    except Exception as e:
        raise DatabaseError(f"Failed to respond to invite: {str(e)}")


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: str,
    current_user: UserResponse = Depends(get_current_user),
    table_service: TableService = Depends(get_table_service),
):
    """Delete a table."""
    try:
        table = await table_service.get_table_by_id(table_id)
        if not table:
            raise ResourceNotFoundError("Table not found")

        # Check if user is the creator
        if table.creator_id != str(current_user.id):
            raise InvalidInputError("Only the creator can delete the table")

        await table_service.delete_table(table_id)
    except Exception as e:
        raise DatabaseError(f"Failed to delete table: {str(e)}")
