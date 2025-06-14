import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.exceptions import DatabaseException
from app.repositories.base import BaseRepository
from app.schemas.game import GameStatusEnum
from app.schemas.table import TableDBInput, TableDBOutput, PlayerStatusEnum, PlayerStatus, TableCountResponse


class TableRepository(BaseRepository[TableDBInput, TableDBOutput]):
    """
    Repository for tables collection.
    
    This repository handles all database operations related to poker tables, including:
    - Table CRUD operations (inherited from BaseRepository)
    - Player invitation and status management
    - Table status management
    - Table listing and filtering
    
    Type Parameters:
        TableDBInput: Pydantic model for table creation/updates
        TableDBOutput: Pydantic model for table responses
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        """
        Initialize the table repository.
        
        Args:
            db_client: MongoDB client instance
        """
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
        
        Args:
            user_id: The ID of the user
            status: Optional table status to filter by
            skip: Number of tables to skip
            limit: Maximum number of tables to return
            
        Returns:
            List[TableDBOutput]: List of tables
            
        Raises:
            DatabaseException: If there's an error listing tables
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            list_filter = {"players.user_id": user_id}
            if status:
                list_filter["status"] = status
            return await self.list(list_filter, skip=skip, limit=limit)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to list tables for user: {str(e)}")

    async def list_created(
            self,
            user_id: str,
            status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> TableCountResponse:
        """
        List tables where user is a player. Optionally filter by status.

        Args:
            user_id: The ID of the user
            status: Optional table status to filter by
            skip: Number of tables to skip
            limit: Maximum number of tables to return

        Returns:
            TableCountResponse: List and count of tables

        Raises:
            DatabaseException: If there's an error listing tables
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            list_filter = {"creator_id": user_id}
            if status:
                list_filter["status"] = status
            tables = await self.list(list_filter, skip=skip, limit=limit)
            count = await self.count(list_filter)
            return TableCountResponse(tables=tables, count=count)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to list tables for user: {str(e)}")

    async def list_invited(
            self,
            user_id: str,
            status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> TableCountResponse:
        """
        List tables where user is a player. Optionally filter by status.

        Args:
            user_id: The ID of the user
            status: Optional table status to filter by
            skip: Number of tables to skip
            limit: Maximum number of tables to return

        Returns:
            TableCountResponse: List and count of tables

        Raises:
            DatabaseException: If there's an error listing tables
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            list_filter = {"creator_id": {"$ne": user_id}, "players.user_id": user_id}
            if status:
                list_filter["status"] = status
            tables = await self.list(list_filter, skip=skip, limit=limit)
            count = await self.count(list_filter)
            return TableCountResponse(tables=tables, count=count)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to list tables for user: {str(e)}")


    async def invite_players(self, table_id: str, players: List[dict]) -> Optional[TableDBOutput]:
        """
        Invite multiple players to a table.
        
        Args:
            table_id: The ID of the table
            players: List of player dictionaries containing user_id and username
            
        Returns:
            Optional[TableDBOutput]: The updated table if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error inviting players
        """
        try:
            if not ObjectId.is_valid(table_id):
                return None
            new_players = [PlayerStatus(
                user_id=player.get("user_id"),
                username=player.get("username"),
                status=PlayerStatusEnum.INVITED
            ).model_dump() for player in players]
            result = await self.collection.update_one(
                {"_id": ObjectId(table_id)},
                {
                    "$push": {
                        "players": {
                            "$each": new_players
                        }
                    },
                    "$set": {
                        "updated_at": datetime.now(UTC)
                    }
                }
            )
            if not result.acknowledged:
                self.logger.error(f"Failed to invite players to table {table_id}")
                return None
            return await self.get_by_id(table_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to invite players: {str(e)}")

    async def respond_to_invite(
            self,
            table_id: str,
            player_id: str,
            status: PlayerStatusEnum
    ) -> Optional[TableDBOutput]:
        """
        Update a player's status in the players array.
        
        Args:
            table_id: The ID of the table
            player_id: The ID of the player
            status: The new status for the player
            
        Returns:
            Optional[TableDBOutput]: The updated table if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error updating player status
        """
        try:
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
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update player status: {str(e)}")

    async def delete_or_cancel(
            self,
            table_id: str,
            cancel: bool = False
    ) -> bool | Optional[TableDBOutput]:
        """
        If cancel=True, set status to CANCELLED, updated_at now.
        If cancel=False, delete document.
        
        Args:
            table_id: The ID of the table
            cancel: Whether to cancel (True) or delete (False) the table
            
        Returns:
            Union[bool, Optional[TableDBOutput]]: 
                - If cancel=True: The updated table if successful, None otherwise
                - If cancel=False: True if deleted successfully, False otherwise
                
        Raises:
            DatabaseException: If there's an error cancelling or deleting the table
        """
        try:
            if not ObjectId.is_valid(table_id):
                return False
            if cancel:
                return await self.update(
                    table_id,
                    {"status": GameStatusEnum.CANCELLED.value, "updated_at": datetime.now(UTC)}
                )
            else:
                return await self.delete(table_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to {'cancel' if cancel else 'delete'} table: {str(e)}")
