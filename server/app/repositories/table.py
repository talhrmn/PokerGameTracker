from datetime import UTC, datetime
from typing import Dict, List, Optional

from app.repositories.base import BaseRepository
from app.schemas.table import (
    PlayerStatus,
    PlayerStatusEnum,
    TableBase,
    TableDBInput,
    TableDBResponse,
)
from app.schemas.user import UserDBInput
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


class TableRepository(BaseRepository[TableDBResponse]):
    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client, "tables")

    async def get_table_by_id(self, table_id: str) -> Optional[TableDBResponse]:
        table = await self.find_one({"_id": ObjectId(table_id)})
        if not table:
            return None
        return TableDBResponse(**table)

    async def create_table(
        self, table: TableBase, current_user: UserDBInput
    ) -> ObjectId:
        creator_id = current_user.id
        new_table = TableDBInput(
            **table.model_dump(by_alias=True),
            creator_id=str(creator_id),
            players=[
                PlayerStatus(
                    user_id=str(creator_id),
                    username=current_user.username,
                    status=PlayerStatusEnum.CONFIRMED,
                )
            ],
        ).model_dump()

        result = await self.insert_one(new_table)
        if not (result.acknowledged and result.inserted_id):
            raise Exception("Database update failed.")
        return result.inserted_id

    async def get_tables(
        self, status: Optional[str] = None, limit: int = 10, skip: int = 0
    ) -> List[TableDBResponse]:
        query = {}
        if status:
            query["status"] = status

        cursor = self.db_client.tables.find(query).skip(skip).limit(limit)
        tables = await cursor.to_list(length=limit)
        return [TableDBResponse(**table) for table in tables]

    async def update_table(self, table_id: str, update_data: Dict) -> None:
        if update_data:
            update_data["updated_at"] = datetime.now(UTC)

            result = await self.update(
                {"_id": ObjectId(table_id)}, {"$set": update_data}
            )

            if not result.acknowledged:
                raise Exception("Database update failed.")

    async def respond_to_invite_table(
        self, table_id: str, player_id: str, status: PlayerStatusEnum
    ) -> None:
        result = await self.update(
            {"_id": ObjectId(table_id), "players.user_id": player_id},
            {"$set": {"players.$.status": status}},
        )

        if not result.acknowledged:
            raise Exception("Database update failed.")

    async def delete_table(self, table_id: str) -> None:
        await self.delete_one({"_id": ObjectId(table_id)})
