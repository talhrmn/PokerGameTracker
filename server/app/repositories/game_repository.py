import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from app.repositories.base import BaseRepository
from app.schemas.game import GameDBInput, GameDBOutput, GameBase, BuyIn, GameStatusEnum
from app.core.exceptions import DatabaseException


class GameRepository(BaseRepository[GameDBInput, GameDBOutput]):
    """
    Repository for games collection.
    
    This repository handles all database operations related to poker games, including:
    - Game CRUD operations (inherited from BaseRepository)
    - Player management (invites, buy-ins, cash-outs)
    - Game statistics and analytics
    - Game listing and filtering
    
    Type Parameters:
        GameDBInput: Pydantic model for game creation/updates
        GameDBOutput: Pydantic model for game responses
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        """
        Initialize the game repository.
        
        Args:
            db_client: MongoDB client instance
        """
        super().__init__(db_client.games, GameDBInput, GameDBOutput)
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_game(self, game_data: GameBase, user_id: str) -> GameDBOutput:
        """
        Create a new game with the given data and creator.
        
        Args:
            game_data: The base game data
            user_id: The ID of the game creator
            
        Returns:
            GameDBOutput: The created game
            
        Raises:
            DatabaseException: If there's an error creating the game
        """
        try:
            game = GameDBInput(**game_data.model_dump(by_alias=True), creator_id=user_id)
            return await self.create(game)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to create game: {str(e)}")

    async def list_for_player(
            self,
            player_id: str,
            table_id: Optional[str] = None,
            status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[GameDBOutput]:
        """
        List games where player is in players.user_id, optionally filter by table_id and status.
        
        Args:
            player_id: The ID of the player
            table_id: Optional table ID to filter by
            status: Optional game status to filter by
            skip: Number of games to skip
            limit: Maximum number of games to return
            
        Returns:
            List[GameDBOutput]: List of games
            
        Raises:
            DatabaseException: If there's an error listing games
        """
        try:
            if not ObjectId.is_valid(player_id):
                return []

            list_filter = {"players.user_id": player_id}
            if table_id and ObjectId.is_valid(table_id):
                list_filter["table_id"] = str(table_id)
            if status:
                list_filter["status"] = status
            return await self.list(list_filter, skip=skip, limit=limit, sort=["date", DESCENDING])
        except Exception as e:
            raise DatabaseException(detail=f"Failed to list games for player: {str(e)}")

    async def count_for_player(self, player_id: str) -> int:
        """
        Count games for a player.
        
        Args:
            player_id: The ID of the player
            
        Returns:
            int: Number of games
            
        Raises:
            DatabaseException: If there's an error counting games
        """
        try:
            if not ObjectId.is_valid(player_id):
                return 0
            count_filter = {"players.user_id": player_id}
            return await self.count(count_filter)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to count games for player: {str(e)}")

    async def count_for_table(self, table_id: str) -> int:
        """
        Count games for a table.
        
        Args:
            table_id: The ID of the table
            
        Returns:
            int: Number of games
            
        Raises:
            DatabaseException: If there's an error counting games
        """
        try:
            if not ObjectId.is_valid(table_id):
                return 0
            count_filter = {"table_id": ObjectId(table_id)}
            return await self.count(count_filter)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to count games for table: {str(e)}")

    async def list_recent_for_player(
            self,
            player_id: str,
            limit: int = 5
    ) -> List[GameDBOutput]:
        """
        List recent games for a player.
        
        Args:
            player_id: The ID of the player
            limit: Maximum number of games to return
            
        Returns:
            List[GameDBOutput]: List of recent games
            
        Raises:
            DatabaseException: If there's an error listing games
        """
        try:
            if not ObjectId.is_valid(player_id):
                return []
            list_filter = {"players.user_id": player_id}
            return await self.list(list_filter, sort=["date", DESCENDING], limit=limit)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to list recent games: {str(e)}")

    async def push_player_invite(
            self,
            game_id: str,
            user_id: str,
            username: str
    ) -> Optional[GameDBOutput]:
        """
        Add player to game.players if not already present.
        
        Args:
            game_id: The ID of the game
            user_id: The ID of the user to invite
            username: The username of the user to invite
            
        Returns:
            Optional[GameDBOutput]: The updated game if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error adding the player
        """
        try:
            if not ObjectId.is_valid(game_id):
                return None
            result = await self.collection.update_one(
                {"_id": ObjectId(game_id), "players.user_id": {"$ne": user_id}},
                {"$push": {
                    "players": {
                        "user_id": user_id,
                        "username": username,
                        "buy_ins": [],
                        "cash_out": 0,
                        "net_profit": 0,
                        "notable_hands": []
                    }
                }}
            )
            if not result.acknowledged:
                self.logger.error(f"Failed to push player invite for game {game_id}, user {user_id}")
                return None
            return await self.get_by_id(game_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to add player to game: {str(e)}")

    async def pull_player(
            self,
            game_id: str,
            user_id: str
    ) -> Optional[GameDBOutput]:
        """
        Remove player from game.players.
        
        Args:
            game_id: The ID of the game
            user_id: The ID of the user to remove
            
        Returns:
            Optional[GameDBOutput]: The updated game if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error removing the player
        """
        try:
            if not ObjectId.is_valid(game_id):
                return None
            result = await self.collection.update_one(
                {"_id": ObjectId(game_id)},
                {"$pull": {"players": {"user_id": user_id}}}
            )
            if not result.acknowledged:
                self.logger.error(f"Failed to pull player {user_id} from game {game_id}")
                return None
            return await self.get_by_id(game_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to remove player from game: {str(e)}")

    async def push_player_buyin(
            self,
            game_id: str,
            player_id: str,
            buyin: BuyIn,
            total_pot: float,
            available_cash_out: float
    ) -> Optional[GameDBOutput]:
        """
        Push a buy-in for player, and update total_pot, available_cash_out.
        
        Args:
            game_id: The ID of the game
            player_id: The ID of the player
            buyin: The buy-in details
            total_pot: The current total pot
            available_cash_out: The current available cash out
            
        Returns:
            Optional[GameDBOutput]: The updated game if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error adding the buy-in
        """
        try:
            if not ObjectId.is_valid(game_id):
                return None
            result = await self.collection.update_one(
                {"_id": ObjectId(game_id), "players.user_id": player_id},
                {
                    "$push": {"players.$.buy_ins": buyin.model_dump()},
                    "$set": {
                        "total_pot": total_pot + buyin.amount,
                        "available_cash_out": available_cash_out + buyin.amount
                    }
                }
            )
            if not result.acknowledged:
                self.logger.error(f"Failed to push buyin for player {player_id} in game {game_id}")
                return None
            return await self.get_by_id(game_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to add buy-in: {str(e)}")

    async def set_player_cashout(
            self,
            game_id: str,
            player_id: str,
            cashout: float,
            net_profit: float,
            available_cash_out: float
    ) -> Optional[GameDBOutput]:
        """
        Update player's cash_out, net_profit, available_cash_out, and updated_at.
        
        Args:
            game_id: The ID of the game
            player_id: The ID of the player
            cashout: The cash out amount
            net_profit: The net profit amount
            available_cash_out: The current available cash out
            
        Returns:
            Optional[GameDBOutput]: The updated game if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error updating the cash out
        """
        try:
            if not ObjectId.is_valid(game_id):
                return None
            result = await self.collection.update_one(
                {"_id": ObjectId(game_id), "players.user_id": player_id},
                {"$set": {
                    "players.$.cash_out": cashout,
                    "players.$.net_profit": net_profit,
                    "available_cash_out": available_cash_out - cashout,
                    "updated_at": datetime.now(UTC)
                }}
            )
            if not result.acknowledged:
                self.logger.error(f"Failed to set cashout for player {player_id} in game {game_id}")
                return None
            return await self.get_by_id(game_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update cash out: {str(e)}")

    async def get_user_stats_rate(self, user_id: str) -> List[dict]:
        """
        Get overall win rate statistics for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[dict]: List containing win rate statistics
            
        Raises:
            DatabaseException: If there's an error getting statistics
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            pipeline_overall = [
                {"$match": {
                    "players.user_id": ObjectId(user_id),
                    "status": GameStatusEnum.COMPLETED.value
                }},
                {"$unwind": "$players"},
                {"$match": {"players.user_id": ObjectId(user_id)}},
                {"$group": {
                    "_id": None,
                    "wins": {"$sum": {"$cond": [{"$gt": ["$players.net_profit", 0]}, 1, 0]}},
                    "total_games": {"$sum": 1}
                }}
            ]
            return await self.collection.aggregate(pipeline_overall).to_list(length=1)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user stats rate: {str(e)}")

    async def get_user_monthly_stats_rates(self, user_id: str) -> List[dict]:
        """
        Get monthly win rate statistics for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[dict]: List containing monthly win rate statistics
            
        Raises:
            DatabaseException: If there's an error getting statistics
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            pipeline_monthly = [
                {"$match": {
                    "players.user_id": ObjectId(user_id),
                    "status": GameStatusEnum.COMPLETED.value
                }},
                {"$unwind": "$players"},
                {"$match": {"players.user_id": ObjectId(user_id)}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m", "date": "$date"}},
                    "wins": {"$sum": {"$cond": [{"$gt": ["$players.net_profit", 0]}, 1, 0]}},
                    "total_games": {"$sum": 1}
                }}
            ]
            return await self.collection.aggregate(pipeline_monthly).to_list(length=100)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user monthly stats rates: {str(e)}")
