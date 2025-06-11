from datetime import datetime, UTC
from typing import Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException, status as status_code
from motor.motor_asyncio import AsyncIOMotorClient

from server.app.schemas.game import GameStatusEnum
from server.app.schemas.table import PlayerStatus, PlayerStatusEnum, TableDBInput, TableBase, TableDBResponse
from server.app.schemas.user import UserDBInput


class TableHandler:

    def __init__(self):
        pass

    @staticmethod
    async def get_table_by_id(table_id: str, db_client: AsyncIOMotorClient) -> Optional[TableDBResponse]:
        table = await db_client.tables.find_one({"_id": ObjectId(table_id)})
        if not table:
            return None
        return TableDBResponse(**table)

    @staticmethod
    async def create_table(table: TableBase, current_user: UserDBInput, db_client: AsyncIOMotorClient) -> ObjectId:
        creator_id = current_user.id
        new_table = TableDBInput(
            **table.model_dump(by_alias=True),
            creator_id=str(creator_id),
            players=[PlayerStatus(user_id=str(creator_id), username=current_user.username,
                                  status=PlayerStatusEnum.CONFIRMED)]
        ).model_dump()

        result = await db_client.tables.insert_one(new_table)
        if not (result.acknowledged and result.inserted_id):
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )
        return result.inserted_id

    @staticmethod
    async def get_tables(status: str, limit: int, skip: int, current_user: UserDBInput,
                         db_client: AsyncIOMotorClient) -> List[TableDBResponse]:
        query = {"players.user_id": current_user.id}
        if status:
            query["status"] = status

        cursor = db_client.tables.find(query).skip(skip).limit(limit)
        tables = await cursor.to_list(length=limit)
        return [TableDBResponse(**table) for table in tables]

    @staticmethod
    async def update_table(table_id: str, update_data: Dict, db_client: AsyncIOMotorClient) -> None:
        if update_data:
            update_data["updated_at"] = datetime.now(UTC)

            result = await db_client.tables.update_one(
                {"_id": ObjectId(table_id)},
                {"$set": update_data}
            )

            if not result.acknowledged:
                raise HTTPException(
                    status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database update failed."
                )

    @staticmethod
    async def respond_to_invite_table(table_id: str, player_id: str, status: PlayerStatusEnum,
                                      db_client: AsyncIOMotorClient) -> None:
        result = await db_client.tables.update_one(
            {"_id": ObjectId(table_id), "players.user_id": player_id},
            {"$set": {"players.$.status": status}},
        )

        if not result.acknowledged:
            raise HTTPException(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed."
            )

    @staticmethod
    async def delete_table(table_id: str, db_client: AsyncIOMotorClient):
        game_count = await db_client.games.count_documents({"table_id": ObjectId(table_id)})

        if game_count > 0:
            await db_client.tables.update_one(
                {"_id": ObjectId(table_id)},
                {"$set": {"status": GameStatusEnum.CANCELLED, "updated_at": datetime.now(UTC)}}
            )
        else:
            await db_client.tables.delete_one({"_id": ObjectId(table_id)})


table_handler = TableHandler()
