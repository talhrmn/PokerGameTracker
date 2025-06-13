# app/services/table_service.py

import logging
from datetime import datetime, UTC
from typing import List, Optional, Dict

from fastapi import HTTPException, status

from app.repositories.table_repository import TableRepository
from app.schemas.table import TableBase, TableDBInput, TableDBOutput, PlayerStatusEnum, PlayerStatus
from app.schemas.user import UserResponse  # or appropriate user schema
from app.services.base import BaseService


class TableService(BaseService[TableDBInput, TableDBOutput]):
    """
    Service layer for table business logic.
    """

    def __init__(self, repository: TableRepository):
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_table(self, table_data: TableBase, current_user: UserResponse) -> TableDBOutput:
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
        try:
            created = await self.repository.create(table_input)
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Table creation failed")
        return created

    async def get_tables(
            self,
            current_user: UserResponse,
            table_status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[TableDBOutput]:
        """
        List tables where current_user is a player, optionally filter by status.
        """
        tables = await self.repository.list_for_user(str(current_user.id), status=table_status, skip=skip, limit=limit)
        return tables

    async def update_table(self, table_id: str, update_data: Dict) -> Optional[TableDBOutput]:
        """
        Update arbitrary fields of a table (e.g., name, venue). Add updated_at timestamp.
        """
        if not update_data:
            return None

        update_data["updated_at"] = datetime.now(UTC)
        updated = await self.repository.update(table_id, update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update table")
        return updated

    async def respond_to_invite(
            self,
            table_id: str,
            player_id: str,
            table_status: PlayerStatusEnum
    ) -> TableDBOutput:
        """
        A user responds to an invite: change their status in the table.
        """
        # Optionally: check that status is one of allowed responses, and that the table exists
        table = await self.get_by_id(table_id)
        # Check that player_id is indeed in the players array
        found = any(str(p.user_id) == player_id for p in table.players)
        if not found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found in table")
        # Update status
        updated = await self.repository.respond_to_invite(table_id, player_id, table_status)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to respond to invite")
        return updated

    async def delete_table(self, table_id: str, game_count: int) -> None:
        """
        Delete or cancel a table. If game_count > 0, cancel; else delete.
        """
        # Optionally: check table exists
        table = await self.get_by_id(table_id)  # raises 404 if not exists
        if game_count > 0:
            ok = await self.repository.delete_or_cancel(table_id, cancel=True)
            if not ok:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel table")
        else:
            ok = await self.repository.delete_or_cancel(table_id, cancel=False)
            if not ok:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete table")

    async def invite_players(
            self,
            table_id: str,
            inviter_user: UserResponse,
            invitees: List[Dict]
    ) -> TableDBOutput:
        """
        Business logic to invite a new player: add to players array with status pending (or similar).
        """
        # Ensure table exists
        table = await self.get_by_id(table_id)
        # Only creator or certain roles may invite; implement your permission logic:
        if str(table.creator_id) != str(inviter_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only creator can invite players")
        # Check invitee not already in players
        table_player_ids = {player.user_id for player in table.players}
        invitees_not_in_table = [p for p in invitees if p.get("user_id") not in table_player_ids]
        updated = await self.repository.invite_players(table_id, invitees_not_in_table)
        return updated
