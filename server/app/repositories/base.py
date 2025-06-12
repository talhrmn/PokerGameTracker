import logging
from typing import Generic, TypeVar, Optional, List, Type

from bson import ObjectId
from pydantic import BaseModel

# TCreate: model used for create (no _id)
# TRead: model used for read/response (includes _id)
TCreate = TypeVar("TCreate", bound=BaseModel)
TRead = TypeVar("TRead", bound=BaseModel)


class BaseRepository(Generic[TCreate, TRead]):
    """
    Generic repository for MongoDB collection.
    - TCreate: Pydantic model class for input/insertion (e.g., UserDBInput)
    - TRead:   Pydantic model class for reading/response (e.g., UserDBResponse)
    """

    def __init__(
            self,
            collection,
            create_model: Type[TCreate],
            read_model: Type[TRead]
    ):
        """
        :param collection: motor collection, e.g. db.users
        :param create_model: Pydantic class for insertion (no _id)
        :param read_model:   Pydantic class for reading/response (with _id alias)
        """
        self.collection = collection
        self.create_model = create_model
        self.read_model = read_model
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_by_id(self, id_str: str) -> Optional[TRead]:
        """Fetch by _id, return read_model instance or None."""
        if not ObjectId.is_valid(id_str):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(id_str)})
        if not doc:
            return None
        try:
            return self.read_model(**doc)
        except Exception as e:
            self.logger.error(f"Error parsing document to {self.read_model}: {e}")
            return None

    async def get_one_by_query(self, query: dict, projection: dict = None, dump_model: bool = True) -> Optional[TRead]:
        """Fetch by _id, return read_model instance or None."""
        doc = await self.collection.find_one(query, projection or {})
        if not doc:
            return None
        if not dump_model: return doc
        try:
            return self.read_model(**doc)
        except Exception as e:
            self.logger.error(f"Error parsing document to {self.read_model}: {e}")
            return None

    async def create(self, obj_in: TCreate) -> TRead:
        """
        Insert new document from obj_in, return read_model instance including generated _id.
        """
        data = obj_in.model_dump(by_alias=True)
        result = await self.collection.insert_one(data)
        if not (result.acknowledged and result.inserted_id):
            self.logger.error(f"Insert not acknowledged or no inserted_id for {obj_in}")
            raise RuntimeError("Database insert failed")
        data["_id"] = result.inserted_id
        try:
            return self.read_model(**data)
        except Exception as e:
            self.logger.error(f"Error constructing {self.read_model} after insert: {e}")
            raise

    async def update(self, id_str: str, update_data: dict) -> Optional[TRead]:
        """
        Update fields via $set; return updated read_model or None if failure/invalid id.
        """
        if not ObjectId.is_valid(id_str) or not update_data:
            return None
        result = await self.collection.update_one(
            {"_id": ObjectId(id_str)},
            {"$set": update_data}
        )
        if not result.acknowledged:
            self.logger.error(f"Update not acknowledged for id {id_str}")
            return None
        return await self.get_by_id(id_str)

    async def delete(self, id_str: str) -> bool:
        """Delete document by _id. Return True if deleted."""
        if not ObjectId.is_valid(id_str):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id_str)})
        if result.deleted_count != 1:
            self.logger.error(f"Delete not acknowledged for id {id_str}")
            return False
        return True

    async def list(
            self,
            filter_: dict = None,
            projection: dict = None,
            skip: int = 0,
            limit: int = 100,
            sort: List = None
    ) -> List[TRead]:
        """
        List documents matching filter_, return list of read_model instances.
        sort: [field, direction]
        """
        cursor = self.collection.find(filter_ or {}, projection or {})
        if sort:
            cursor = cursor.sort(sort[0], sort[1])
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        docs = await cursor.to_list(length=limit)
        results: List[TRead] = []
        for doc in docs:
            try:
                results.append(self.read_model(**doc))
            except Exception as e:
                self.logger.error(f"Error parsing document in list to {self.read_model}: {e}")
        return results

    async def count(self, filter_: dict = None) -> int:
        """Count documents matching filter_."""
        return await self.collection.count_documents(filter_ or {})
