from datetime import UTC, datetime
from typing import Dict, List, Optional

from app.repositories.base import BaseRepository
from app.schemas.game import BuyIn, GameBase, GameDBInput, GameDBResponse
from app.schemas.table import PlayerStatusEnum
from app.schemas.user import UserResponse
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.exceptions import DatabaseError
from app.schemas.py_object_id import PyObjectId


class GameRepository(BaseRepository[GameDBResponse]):
    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client, "games")

    async def get_game_by_id(self, game_id: str) -> Optional[GameDBResponse]:
        game = await self.find_one({"_id": ObjectId(game_id)})
        if not game:
            return None
        return GameDBResponse(**game)

    async def create_game(self, game: GameBase, user: UserResponse) -> ObjectId:
        new_game = GameDBInput(
            **game.model_dump(by_alias=True),
            creator_id=str(user.id),
            players=[
                {
                    "user_id": str(user.id),
                    "username": user.username,
                    "status": PlayerStatusEnum.CONFIRMED,
                    "buy_ins": [],
                    "cash_out": 0,
                    "net_profit": 0,
                    "notable_hands": [],
                }
            ],
        ).model_dump()

        result = await self.create(new_game)
        if not result:
            raise Exception("Database update failed.")
        return result["_id"]

    async def update_game_invite(
        self, game_id: str, user: UserResponse, status: PlayerStatusEnum
    ) -> None:
        query = {"_id": ObjectId(game_id)}
        if status == PlayerStatusEnum.CONFIRMED:
            query["players.user_id"] = {"$ne": str(user.id)}
            action = {
                "$push": {
                    "players": {
                        "user_id": str(user.id),
                        "username": user.username,
                        "buy_ins": [],
                        "cash_out": 0,
                        "net_profit": 0,
                        "notable_hands": [],
                    }
                }
            }
        else:
            action = {"$pull": {"players": {"user_id": str(user.id)}}}

        result = await self.update(query, action)
        if not result:
            raise Exception("Database update failed.")

    async def update_player_buyin(
        self,
        game_id: str,
        player_id: str,
        buyin: BuyIn,
        total_pot: float,
        available_cash_out: float,
    ) -> None:
        result = await self.update(
            {"_id": ObjectId(game_id), "players.user_id": player_id},
            {
                "$push": {"players.$.buy_ins": buyin.model_dump()},
                "$set": {
                    "total_pot": total_pot + buyin.amount,
                    "available_cash_out": available_cash_out + buyin.amount,
                    "updated_at": datetime.now(UTC),
                },
            },
        )

        if not result:
            raise Exception("Database update failed.")

    async def update_player_cashout(
        self,
        game_id: str,
        player_id: str,
        cashout: float,
        net_profit: float,
        available_cash_out: float,
    ) -> None:
        result = await self.update(
            {"_id": ObjectId(game_id), "players.user_id": player_id},
            {
                "$set": {
                    "players.$.cash_out": cashout,
                    "players.$.net_profit": net_profit,
                    "available_cash_out": available_cash_out - cashout,
                    "updated_at": datetime.now(UTC),
                }
            },
        )

        if not result:
            raise Exception("Database update failed.")

    async def get_games_for_player(
        self,
        player: UserResponse,
        table_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[GameDBResponse]:
        query = {"players.user_id": str(player.id)}

        if table_id and ObjectId.is_valid(table_id):
            query["table_id"] = ObjectId(table_id)

        if status:
            query["status"] = status

        games = await self.find_many(query)
        games.sort(key=lambda x: x["date"], reverse=True)

        if skip:
            games = games[skip:]
        if limit:
            games = games[:limit]

        return [GameDBResponse(**game) for game in games]

    async def get_games_count_for_player(self, player: UserResponse) -> int:
        games = await self.find_many({"players.user_id": str(player.id)})
        return len(games)

    async def update_game(self, game_id: str, update_data: Dict) -> None:
        if update_data:
            update_data["updated_at"] = datetime.now(UTC)

            result = await self.update(
                {"_id": ObjectId(game_id)}, {"$set": update_data}
            )

            if not result:
                raise Exception("Database update failed.")

    async def get_recent_games(self, user_id: str, limit: int) -> List[GameDBResponse]:
        games = await self.find_many({"players.user_id": user_id})
        games.sort(key=lambda x: x["date"], reverse=True)
        games = games[:limit]
        return [GameDBResponse(**game) for game in games]

    async def count_games_for_table(self, table_id: str) -> int:
        """Count games for a table."""
        try:
            return await self.count({"table_id": PyObjectId(table_id)})
        except Exception as e:
            raise DatabaseError(f"Failed to count games: {str(e)}")
