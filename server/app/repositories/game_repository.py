# app/repositories/game_repository.py

import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from app.repositories.base import BaseRepository
from app.schemas.game import GameDBInput, GameDBOutput, GameBase, BuyIn, GameStatusEnum


class GameRepository(BaseRepository[GameDBInput, GameDBOutput]):
    """
    Repository for `games` collection.
    - TCreate: GameDBInput
    - TRead:   GameDBResponse
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client.games, GameDBInput, GameDBOutput)
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    # get_by_id, create (in BaseRepository) can be used, but create_game often needs business logic, so service may call base.create

    async def create_game(self, game_data: GameBase, user_id: str) -> GameDBOutput:
        game = GameDBInput(**game_data.model_dump(by_alias=True), creator_id=user_id)
        result = await self.create(game)
        return result

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
        """
        if not ObjectId.is_valid(player_id):
            return []

        list_filter = {"players.user_id": player_id}
        if table_id and ObjectId.is_valid(table_id):
            list_filter["table_id"] = str(table_id)
        if status:
            list_filter["status"] = status
        results = await self.list(list_filter, skip=skip, limit=limit, sort=["date", DESCENDING])
        return results

    async def count_for_player(self, player_id: str) -> int:
        if not ObjectId.is_valid(player_id):
            return 0
        count_filter = {"players.user_id": player_id}
        return await self.count(count_filter)

    async def count_for_table(self, table_id: str) -> int:
        if not ObjectId.is_valid(table_id):
            return 0
        count_filter = {"table_id": ObjectId(table_id)}
        return await self.count(count_filter)

    async def list_recent_for_player(
            self,
            player_id: str,
            limit: int = 5
    ) -> List[GameDBOutput]:
        if not ObjectId.is_valid(player_id):
            return []
        list_filter = {"players.user_id": player_id}
        results = await self.list(list_filter, sort=["date", DESCENDING], limit=limit)
        return results

    # The following are lower-level DB update helpers; service layer orchestrates business logic.

    async def push_player_invite(
            self,
            game_id: str,
            user_id: str,
            username: str
    ) -> Optional[GameDBOutput]:
        """
        Add player to game.players if not already present.
        """
        if not ObjectId.is_valid(game_id):
            return None
        # Only push if not present: similar to original: status handling in service
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

    async def pull_player(
            self,
            game_id: str,
            user_id: str
    ) -> Optional[GameDBOutput]:
        """
        Remove player from game.players.
        """
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
        """
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
        """
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

    async def get_user_stats_rate(self, user_id: str):
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
        result = await self.collection.aggregate(pipeline_overall).to_list(length=1)
        return result

    async def get_user_monthly_stats_rates(self, user_id: str):
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
        results = await self.collection.aggregate(pipeline_monthly).to_list(length=100)
        return results