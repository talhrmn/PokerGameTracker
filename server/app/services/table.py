import logging
from datetime import UTC, datetime
from typing import Dict, List, Optional

from app.core.exceptions import (
    DatabaseError,
    InvalidInputError,
    ResourceNotFoundError,
    TableStateError,
)
from app.db.mongo_client import AsyncIOMotorClient
from app.repositories.game import GameRepository
from app.repositories.table import TableRepository
from app.schemas.game import GameStatusEnum
from app.schemas.table import PlayerStatus, PlayerStatusEnum, TableBase, TableDBResponse, Table, TableCreate, TableUpdate
from app.schemas.user import UserDBInput
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class TableService(BaseService):
    def __init__(
        self,
        db_client: AsyncIOMotorClient,
        game_repository: GameRepository,
    ):
        super().__init__(TableRepository(db_client))
        self.game_repository = game_repository

    async def get_table_by_id(self, table_id: str) -> Optional[TableDBResponse]:
        """Get a table by ID."""
        try:
            return await self.repository.get_table_by_id(table_id)
        except Exception as e:
            raise DatabaseError(f"Failed to get table: {str(e)}")

    async def create_table(self, table: TableCreate, current_user: UserDBInput) -> TableDBResponse:
        """Create a new table."""
        try:
            table_id = await self.repository.create_table(table, current_user)
            created_table = await self.get_table_by_id(str(table_id))
            if not created_table:
                raise DatabaseError("Failed to retrieve created table")
            return created_table
        except Exception as e:
            raise DatabaseError(f"Failed to create table: {str(e)}")

    async def get_tables(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[TableDBResponse]:
        try:
            return await self.repository.get_tables(status, limit or 10, skip or 0)
        except Exception as e:
            logger.error(f"Failed to get tables: {str(e)}")
            raise DatabaseError(f"Failed to get tables: {str(e)}")

    async def update_table(
        self, table_id: str, table_update: TableUpdate, user_id: str
    ) -> TableDBResponse:
        """Update a table."""
        try:
            table = await self.get_table_by_id(table_id)
            if not table:
                raise ResourceNotFoundError("Table not found")

            # Validate user is table creator
            if str(table.created_by) != str(user_id):
                raise InvalidInputError("Only table creator can update table")

            # Update table
            updated_table = await self.repository.update_table(table_id, table_update)

            # If table has a game, update game status if needed
            if table.game_id:
                game_update = table_update.get("status")
                if game_update:
                    await self.game_repository.update_game(
                        table.game_id, {"status": game_update}
                    )

            return updated_table
        except Exception as e:
            raise DatabaseError(f"Failed to update table: {str(e)}")

    async def respond_to_invite_table(
        self, table_id: str, player_id: str, status: PlayerStatusEnum
    ) -> TableDBResponse:
        try:
            # Get existing table to check game status
            existing_table = await self.get_table_by_id(table_id)
            if not existing_table:
                raise ResourceNotFoundError("Table not found")

            # Update player status
            await self.repository.respond_to_invite_table(table_id, player_id, status)

            # If table has a game, update game invite status
            if existing_table.game_id:
                await self.game_repository.update_game_invite(
                    existing_table.game_id, player_id, status
                )

            # Get and return updated table
            updated_table = await self.get_table_by_id(table_id)
            if not updated_table:
                raise DatabaseError("Failed to retrieve updated table")
            return updated_table
        except Exception as e:
            logger.error(
                f"Failed to respond to table invite for table {table_id} and player {player_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to respond to table invite: {str(e)}")

    async def delete_table(self, table_id: str) -> None:
        try:
            # Check if table has any games
            game_count = await self.game_repository.count_games_for_table(table_id)

            if game_count > 0:
                # If table has games, mark it as cancelled
                await self.repository.update_table(
                    table_id,
                    {
                        "status": GameStatusEnum.CANCELLED,
                        "updated_at": datetime.now(UTC),
                    },
                )
            else:
                # If no games, delete the table
                await self.repository.delete_table(table_id)
        except Exception as e:
            logger.error(f"Failed to delete table {table_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete table: {str(e)}")

    async def validate_table_access(self, table: TableDBResponse, user_id: str) -> None:
        """Validate if a user has access to a table."""
        if not table:
            raise ResourceNotFoundError("Table not found")

        user_is_player = any(player.user_id == str(user_id) for player in table.players)
        user_is_creator = str(table.creator_id) == str(user_id)

        if not (user_is_player or user_is_creator):
            raise InvalidInputError("Access denied")

    async def validate_table_creator(self, table: Table, user_id: str) -> None:
        """Validate that a user is the creator of a table."""
        if str(table.created_by) != str(user_id):
            raise InvalidInputError("Only table creator can perform this action")

    async def validate_table_state(
        self, table: TableDBResponse, required_status: Optional[GameStatusEnum] = None
    ) -> None:
        """Validate if a table is in the required state for an operation."""
        if not table:
            raise ResourceNotFoundError("Table not found")

        if required_status and table.status != required_status:
            raise TableStateError(
                f"Table must be in {required_status} state for this operation"
            )

    async def invite_player(self, table_id: str, user_id: str) -> TableDBResponse:
        """Invite a player to a table."""
        try:
            table = await self.get_table_by_id(table_id)
            if not table:
                raise ResourceNotFoundError("Table not found")

            # Check if player is already in the table
            if any(player.user_id == user_id for player in table.players):
                raise InvalidInputError("Player is already in the table")

            # Add player to table
            players = table.players.copy()
            players.append(
                PlayerStatus(user_id=user_id, status=PlayerStatusEnum.INVITED)
            )

            # Update table
            await self.repository.update_table(table_id, {"players": players})

            # Get and return updated table
            updated_table = await self.get_table_by_id(table_id)
            if not updated_table:
                raise DatabaseError("Failed to retrieve updated table")
            return updated_table
        except Exception as e:
            logger.error(
                f"Failed to invite player {user_id} to table {table_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to invite player: {str(e)}")

    async def get_tables_for_user(self, user_id: str) -> List[Table]:
        """Get tables for a user."""
        try:
            return await self.repository.get_tables_for_user(user_id)
        except Exception as e:
            raise DatabaseError(f"Failed to get tables: {str(e)}")
