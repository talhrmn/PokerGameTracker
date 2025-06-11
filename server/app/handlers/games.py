from datetime import datetime, UTC
from typing import Optional, Dict, List

from bson import ObjectId
from fastapi import HTTPException, status as status_code
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from server.app.handlers.tables import table_handler
from server.app.handlers.users import user_handler
from server.app.schemas.game import GameDBInput, GameUpdate, GameStatusEnum, GameBase, GameDBResponse, BuyIn, Duration
from server.app.schemas.table import PlayerStatusEnum
from server.app.schemas.user import UserStats, MonthlyStats, UserResponse


class GameHandler:

    def __init__(self):
        pass

    @staticmethod
    async def get_game_by_id(game_id: str, db_client: AsyncIOMotorClient) -> Optional[GameDBResponse]:
        game = await db_client.games.find_one({"_id": ObjectId(game_id)})
        if not game:
            return None
        return GameDBResponse(**game)

    @staticmethod
    async def create_game(game: GameBase, user: UserResponse, db_client: AsyncIOMotorClient) -> GameDBResponse:
        new_game = GameDBInput(**game.model_dump(by_alias=True), creator_id=str(user.id)).model_dump()
        result = await db_client.games.insert_one(new_game)

        if not (result.acknowledged and result.inserted_id):
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )
        return GameDBResponse(**new_game)

    @staticmethod
    async def update_game_invite(game_id: str, user: UserResponse, status: PlayerStatusEnum,
                                 db_client: AsyncIOMotorClient) -> None:
        query = {"_id": ObjectId(game_id)}
        if status == PlayerStatusEnum.CONFIRMED:
            query["players.user_id"] = {"$ne": user.id}
            action = {
                "$push": {
                    "players": {
                        "user_id": user.id,
                        "username": user.username,
                        "buy_ins": [],
                        "cash_out": 0,
                        "net_profit": 0,
                        "notable_hands": []
                    }
                }
            }
        else:
            action = {
                "$pull": {
                    "players": {"user_id": user.id}
                }
            }

        result = await db_client.games.update_one(query, action)

        if not result.acknowledged:
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )

    @staticmethod
    async def update_player_buyin(game_id: str, player_id: str, buyin: BuyIn, total_pot: float,
                                  available_cash_out: float, db_client: AsyncIOMotorClient) -> None:
        result = await db_client.games.update_one(
            {
                "_id": ObjectId(game_id),
                "players.user_id": player_id
            },
            {
                "$push": {
                    "players.$.buy_ins": buyin.model_dump()
                },
                "$set": {
                    "total_pot": total_pot + buyin.amount,
                    "available_cash_out": available_cash_out + buyin.amount
                }
            }
        )

        if not result.acknowledged:
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )

    @staticmethod
    async def update_player_casheout(game_id: str, player_id: str, cashout: float, net_profit: float,
                                     available_cash_out: float, db_client: AsyncIOMotorClient) -> None:
        result = await db_client.games.update_one(
            {
                "_id": ObjectId(game_id),
                "players.user_id": player_id
            },
            {
                "$set": {
                    "players.$.cash_out": cashout,
                    "players.$.net_profit": net_profit,
                    "available_cash_out": available_cash_out - cashout,
                    "updated_at": datetime.now(UTC)
                }
            }
        )

        if not result.acknowledged:
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )

    @staticmethod
    async def get_games_for_player(player: UserResponse, db_client: AsyncIOMotorClient,
                                   table_id: Optional[str] = None, status: Optional[str] = None,
                                   skip: Optional[int] = None, limit: Optional[int] = None) -> List[GameDBResponse]:
        query = {"players.user_id": player.id}

        if table_id and ObjectId.is_valid(table_id):
            query["table_id"] = str(table_id)

        if status:
            query["status"] = status

        cursor = db_client.games.find(query).sort("date", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        games = await cursor.to_list(length=limit)
        return [GameDBResponse(**game) for game in games]

    @staticmethod
    async def get_games_count_for_player(player: UserResponse, db_client: AsyncIOMotorClient) -> int:
        return await db_client.games.count_documents({"players.user_id": player.id})

    @staticmethod
    async def update_game(game_id: str, update_data: Dict, existing_game: GameDBInput, db_client: AsyncIOMotorClient):
        if update_data:
            update_data["updated_at"] = datetime.now(UTC)

            result = await db_client.games.update_one(
                {"_id": ObjectId(game_id)},
                {"$set": update_data}
            )

            if not result.acknowledged:
                raise HTTPException(
                    status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database update failed."
                )

            game_update = GameUpdate(**update_data)
            if game_update.status == GameStatusEnum.COMPLETED and existing_game.status != GameStatusEnum.COMPLETED:
                await table_handler.update_table(table_id=existing_game.table_id,
                                                 update_data={"status": GameStatusEnum.COMPLETED},
                                                 db_client=db_client)

                for player in existing_game.players:
                    user_id = player.user_id
                    profit = player.net_profit

                    duration = existing_game.duration or Duration()
                    hours_played = duration.hours + (duration.minutes / 60)
                    user_stats = UserStats(
                        total_profit=profit,
                        tables_played=1,
                        hours_played=hours_played
                    )

                    await user_handler.update_user_stats(user_id=user_id, user_inc=user_stats, stats_type="stats",
                                                         db_client=db_client)

                    month = existing_game.date.strftime("%b %Y")

                    user_monthly_stats = MonthlyStats(
                        month=month,
                        profit=profit,
                        win_rate=0,
                        tables_played=1,
                        hours_played=hours_played
                    )
                    await user_handler.update_user_monthly_stats(user_id=user_id, month=month,
                                                                 user_inc=user_monthly_stats, db_client=db_client)

    @staticmethod
    async def get_recent_games(user_id: str, limit: int, db_client: AsyncIOMotorClient) -> List[GameDBResponse]:
        recent_games_cursor = db_client.games.find(
            {"players.user_id": user_id}
        ).sort("date", DESCENDING).limit(limit)

        recent_games = await recent_games_cursor.to_list(length=5)
        return [GameDBResponse(**game) for game in recent_games]


game_handler = GameHandler()
