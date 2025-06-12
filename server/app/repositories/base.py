from typing import Any, Dict, Generic, List, Optional, TypeVar

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import DatabaseError
from app.schemas.py_object_id import PyObjectId

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db_client: AsyncIOMotorClient, collection_name: str):
        self.db = db_client[collection_name]
        self.collection_name = collection_name

    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new document."""
        try:
            result = await self.db.insert_one(data)
            return await self.get_by_id(str(result.inserted_id))
        except DuplicateKeyError as e:
            raise DatabaseError(f"Duplicate key error: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Failed to create document: {str(e)}")

    async def get_by_id(self, id: str) -> Optional[T]:
        """Get a document by ID."""
        try:
            result = await self.db.find_one({"_id": PyObjectId(id)})
            return result
        except Exception as e:
            raise DatabaseError(f"Failed to get document: {str(e)}")

    async def update(self, id: str, data: Dict[str, Any]) -> T:
        """Update a document."""
        try:
            await self.db.update_one(
                {"_id": PyObjectId(id)}, {"$set": data}
            )
            return await self.get_by_id(id)
        except Exception as e:
            raise DatabaseError(f"Failed to update document: {str(e)}")

    async def delete(self, id: str) -> bool:
        """Delete a document."""
        try:
            result = await self.db.delete_one({"_id": PyObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to delete document: {str(e)}")

    async def find(
        self,
        query: Dict[str, Any],
        sort: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[T]:
        """Find documents matching query."""
        try:
            cursor = self.db.find(query)
            if sort:
                cursor = cursor.sort(
                    [(k, ASCENDING if v == 1 else DESCENDING) for k, v in sort.items()]
                )
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return await cursor.to_list(length=None)
        except Exception as e:
            raise DatabaseError(f"Failed to find documents: {str(e)}")

    async def count(self, query: Dict[str, Any]) -> int:
        """Count documents matching query."""
        try:
            return await self.db.count_documents(query)
        except Exception as e:
            raise DatabaseError(f"Failed to count documents: {str(e)}")
