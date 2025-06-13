# app/repositories/table_repository.py

import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.repositories.base import BaseRepository
from app.schemas.game import GameStatusEnum
from app.schemas.table import TableDBInput, TableDBOutput, PlayerStatusEnum, PlayerStatus


class TableRepository(BaseRepository[TableDBInput, TableDBOutput]):
    """
    Repository for `tables` collection.
    - TCreate: TableDBInput (for insertion)
    - TRead:   TableDBResponse (for reads)
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client.tables, TableDBInput, TableDBOutput)
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def list_for_user(
            self,
            user_id: str,
            status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[TableDBOutput]:
        """
        List tables where user is a player. Optionally filter by status.
        """
        if not ObjectId.is_valid(user_id):
            return []
        list_filter = {"players.user_id": user_id}
        if status:
            list_filter["status"] = status

        result = await self.list(list_filter, skip=skip, limit=limit)
        return result

    async def invite_players(self, table_id: str, players: List[dict]) -> Optional[TableDBOutput]:
        new_players = [PlayerStatus(
            user_id=player.get("user_id"),
            username=player.get("username"),
            status=PlayerStatusEnum.INVITED
        ).model_dump() for player in players]
        # Use repository to push into array and update updated_at
        update_data = {"updated_at": datetime.now(UTC)}
        result = await self.collection.update_one(
            {"_id": ObjectId(table_id)},
            {
                # Push multiple items into the "players" array
                "$push": {
                    "players": {
                        "$each": new_players
                    }
                },
                # Update other fields as before
                "$set": {
                    "updated_at": update_data["updated_at"]
                }
            }
        )
        if not result.acknowledged:
            self.logger.error(f"Failed to update player status for table {table_id}, player {player_id}")
            return None
        return await self.get_by_id(table_id)

    async def respond_to_invite(
            self,
            table_id: str,
            player_id: str,
            status: PlayerStatusEnum
    ) -> Optional[TableDBOutput]:
        """
        Update a player's status in the players array.
        """
        if not ObjectId.is_valid(table_id):
            return None
        result = await self.collection.update_one(
            {"_id": ObjectId(table_id), "players.user_id": player_id},
            {"$set": {"players.$.status": status.value if hasattr(status, "value") else status}}
        )
        if not result.acknowledged:
            self.logger.error(f"Failed to update player status for table {table_id}, player {player_id}")
            return None
        return await self.get_by_id(table_id)

    async def delete_or_cancel(
            self,
            table_id: str,
            cancel: bool = False
    ) -> bool | Optional[TableDBOutput]:
        """
        If cancel=True, set status to CANCELLED, updated_at now.
        If cancel=False, delete document.
        Return True if operation succeeded (acknowledged or deleted).
        """
        if not ObjectId.is_valid(table_id):
            return False
        if cancel:
            return await self.update(table_id,
                                     {"status": GameStatusEnum.CANCELLED.value, "updated_at": datetime.now(UTC)})
        else:
            return await self.delete(table_id)
