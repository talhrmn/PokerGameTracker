import logging
from datetime import datetime, UTC
from typing import List, Optional, Dict

from app.core.exceptions import (
    DatabaseException,
    NotFoundException,
    PermissionDeniedException
)
from app.repositories.table_repository import TableRepository
from app.schemas.table import TableBase, TableDBInput, TableDBOutput, PlayerStatusEnum, PlayerStatus, TableCountResponse
from app.schemas.user import UserResponse
from app.services.base import BaseService


class TableService(BaseService[TableDBInput, TableDBOutput]):
    """
    Service for table-related business logic.
    
    This service handles all table-related operations, including:
    - Table creation and management
    - Player invitations and status updates
    - Table status management
    - Table deletion and cancellation
    
    Type Parameters:
        TableDBInput: Pydantic model for table input/creation
        TableDBOutput: Pydantic model for table responses
    """

    def __init__(self, repository: TableRepository):
        """
        Initialize the table service.
        
        Args:
            repository: TableRepository instance for database operations
        """
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_table(self, table_data: TableBase, current_user: UserResponse) -> TableDBOutput:
        """
        Create a new table with the current user as the creator and first player.
        
        Args:
            table_data: The table data to create
            current_user: The user creating the table
            
        Returns:
            TableDBOutput: The created table
            
        Raises:
            DatabaseException: If there's an error creating the table
        """
        try:
            initial_player = PlayerStatus(
                user_id=current_user.id,
                username=current_user.username,
                status=PlayerStatusEnum.CONFIRMED
            )

            table_input = TableDBInput(
                **table_data.model_dump(by_alias=True),
                creator_id=current_user.id,
                players=[initial_player],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            return await self.repository.create(table_input)
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise DatabaseException(detail="Table creation failed")

    async def get_tables(
            self,
            current_user: UserResponse,
            table_status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[TableDBOutput]:
        """
        Get tables where the current user is a player.
        
        Args:
            current_user: The user to get tables for
            table_status: Optional status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[TableDBOutput]: List of tables matching the criteria
            
        Raises:
            DatabaseException: If there's an error fetching tables
        """
        try:
            return await self.repository.list_for_user(
                str(current_user.id),
                status=table_status,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get tables: {str(e)}")

    async def get_created_tables(
            self,
            current_user: UserResponse,
            table_status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> TableCountResponse:
        """
        Get created tables where the current user is a player.

        Args:
            current_user: The user to get tables for
            table_status: Optional status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[TableDBOutput]: List of tables matching the criteria

        Raises:
            DatabaseException: If there's an error fetching tables
        """
        try:
            return await self.repository.list_created(
                str(current_user.id),
                status=table_status,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get tables: {str(e)}")

    async def get_invited_tables(
            self,
            current_user: UserResponse,
            table_status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> TableCountResponse:
        """
        Get tables where the current user is a player.

        Args:
            current_user: The user to get tables for
            table_status: Optional status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[TableDBOutput]: List of tables matching the criteria

        Raises:
            DatabaseException: If there's an error fetching tables
        """
        try:
            return await self.repository.list_invited(
                str(current_user.id),
                status=table_status,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get tables: {str(e)}")


    async def count_tables_for_player(self, current_user: UserResponse) -> TableCountResponse:
        """
        Count total tables for a player.

        Args:
            current_user: The user to count tables for

        Returns:
            int: Total number of tables

        Raises:
            DatabaseException: If there's an error counting tables
        """
        try:
            user_tables = await self.repository.count_created(str(current_user.id))
            invited_tables = await self.repository.count_invited(str(current_user.id))
            return TableCountResponse(created=user_tables, invited=invited_tables)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to count tables for player: {str(e)}")

    async def update_table(self, table_id: str, update_data: Dict) -> Optional[TableDBOutput]:
        """
        Update table fields.
        
        Args:
            table_id: The ID of the table to update
            update_data: Dictionary of fields to update
            
        Returns:
            Optional[TableDBOutput]: The updated table if successful, None if no updates
            
        Raises:
            NotFoundException: If table not found
            DatabaseException: If there's an error updating the table
        """
        try:
            if not update_data:
                return None

            table = await self.get_by_id(table_id)
            if not table:
                raise NotFoundException(detail="Table not found")

            update_data["updated_at"] = datetime.now(UTC)
            updated = await self.update(table_id, update_data)
            if not updated:
                raise DatabaseException(detail="Failed to update table")
            return updated
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update table: {str(e)}")

    async def respond_to_invite(
            self,
            table_id: str,
            player_id: str,
            table_status: PlayerStatusEnum
    ) -> TableDBOutput:
        """
        Update a player's status in response to a table invitation.
        
        Args:
            table_id: The ID of the table
            player_id: The ID of the player responding
            table_status: The new status for the player
            
        Returns:
            TableDBOutput: The updated table
            
        Raises:
            NotFoundException: If table not found or player not in table
            DatabaseException: If there's an error updating the status
        """
        try:
            table = await self.get_by_id(table_id)
            if not table:
                raise NotFoundException(detail="Table not found")

            found = any(str(p.user_id) == player_id for p in table.players)
            if not found:
                raise NotFoundException(detail="Player not found in table")

            updated = await self.repository.respond_to_invite(table_id, player_id, table_status)
            if not updated:
                raise DatabaseException(detail="Failed to respond to invite")
            return updated
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to respond to invite: {str(e)}")

    async def delete_table(self, table_id: str, game_count: int) -> None:
        """
        Delete or cancel a table based on game count.
        
        Args:
            table_id: The ID of the table
            game_count: Number of games associated with the table
            
        Raises:
            NotFoundException: If table not found
            DatabaseException: If there's an error deleting/canceling the table
        """
        try:
            table = await self.get_by_id(table_id)
            if not table:
                raise NotFoundException(detail="Table not found")

            if game_count > 0:
                ok = await self.repository.delete_or_cancel(table_id, cancel=True)
                if not ok:
                    raise DatabaseException(detail="Failed to cancel table")
            else:
                ok = await self.repository.delete_or_cancel(table_id, cancel=False)
                if not ok:
                    raise DatabaseException(detail="Failed to delete table")
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to delete/cancel table: {str(e)}")

    async def invite_players(
            self,
            table_id: str,
            inviter_user: UserResponse,
            invitees: List[Dict]
    ) -> TableDBOutput:
        """
        Invite new players to a table.
        
        Args:
            table_id: The ID of the table
            inviter_user: The user sending the invitations
            invitees: List of users to invite
            
        Returns:
            TableDBOutput: The updated table
            
        Raises:
            NotFoundException: If table not found
            PermissionDeniedException: If inviter is not the table creator
            DatabaseException: If there's an error inviting players
        """
        try:
            table = await self.get_by_id(table_id)
            if not table:
                raise NotFoundException(detail="Table not found")

            if str(table.creator_id) != str(inviter_user.id):
                raise PermissionDeniedException(detail="Only creator can invite players")

            table_player_ids = {player.user_id for player in table.players}
            invitees_not_in_table = [p for p in invitees if p.get("user_id") not in table_player_ids]
            updated = await self.repository.invite_players(table_id, invitees_not_in_table)
            if not updated:
                raise DatabaseException(detail="Failed to invite players")
            return updated
        except (NotFoundException, PermissionDeniedException):
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to invite players: {str(e)}")
