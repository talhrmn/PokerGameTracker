import logging
from typing import Generic, TypeVar, Optional, List, Type, Any, Dict

from bson import ObjectId
from pydantic import BaseModel

from app.core.exceptions import DatabaseException

# TCreate: model used for create (no _id)
# TRead: model used for read/response (includes _id)
TCreate = TypeVar("TCreate", bound=BaseModel)
TRead = TypeVar("TRead", bound=BaseModel)


class BaseRepository(Generic[TCreate, TRead]):
    """
    Generic repository for MongoDB collection.
    
    This base repository provides common CRUD operations for MongoDB collections.
    It uses Pydantic models for type safety and validation.
    
    Type Parameters:
        TCreate: Pydantic model class for input/insertion (e.g., UserDBInput)
        TRead: Pydantic model class for reading/response (e.g., UserDBResponse)
    """

    def __init__(
            self,
            collection,
            create_model: Type[TCreate],
            read_model: Type[TRead]
    ):
        """
        Initialize the repository with MongoDB collection and Pydantic models.
        
        Args:
            collection: Motor MongoDB collection instance (e.g., db.users)
            create_model: Pydantic class for insertion (no _id)
            read_model: Pydantic class for reading/response (with _id alias)
        """
        self.collection = collection
        self.create_model = create_model
        self.read_model = read_model
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_by_id(self, id_str: str) -> Optional[TRead]:
        """
        Fetch a document by its ID.
        
        Args:
            id_str: The string representation of the document's _id
            
        Returns:
            Optional[TRead]: The document as a Pydantic model, or None if not found
            
        Raises:
            DatabaseException: If there's an error accessing the database
        """
        try:
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
        except Exception as e:
            self.logger.error(f"Database error in get_by_id: {e}")
            raise DatabaseException(detail=f"Failed to fetch document by ID: {str(e)}")

    async def get_one_by_query(self, query: dict, projection: dict = None, dump_model: bool = True) -> Optional[TRead]:
        """
        Fetch a single document matching the query.
        
        Args:
            query: MongoDB query dictionary
            projection: Optional projection dictionary
            dump_model: If True, convert to Pydantic model; if False, return raw document
            
        Returns:
            Optional[TRead]: The document as a Pydantic model (or raw dict if dump_model=False), or None if not found
            
        Raises:
            DatabaseException: If there's an error accessing the database
        """
        try:
            doc = await self.collection.find_one(query, projection or {})
            if not doc:
                return None
            if not dump_model:
                return doc
            try:
                return self.read_model(**doc)
            except Exception as e:
                self.logger.error(f"Error parsing document to {self.read_model}: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Database error in get_one_by_query: {e}")
            raise DatabaseException(detail=f"Failed to fetch document: {str(e)}")

    async def create(self, obj_in: TCreate) -> TRead:
        """
        Create a new document from the input model.
        
        Args:
            obj_in: The Pydantic model to create the document from
            
        Returns:
            TRead: The created document as a Pydantic model
            
        Raises:
            DatabaseException: If there's an error creating the document
        """
        try:
            data = obj_in.model_dump(by_alias=True)
            result = await self.collection.insert_one(data)
            if not (result.acknowledged and result.inserted_id):
                self.logger.error(f"Insert not acknowledged or no inserted_id for {obj_in}")
                raise DatabaseException(detail="Database insert failed")
            data["_id"] = result.inserted_id
            try:
                return self.read_model(**data)
            except Exception as e:
                self.logger.error(f"Error constructing {self.read_model} after insert: {e}")
                raise DatabaseException(detail=f"Failed to parse created document: {str(e)}")
        except DatabaseException:
            raise
        except Exception as e:
            self.logger.error(f"Database error in create: {e}")
            raise DatabaseException(detail=f"Failed to create document: {str(e)}")

    async def update(self, id_str: str, update_data: dict) -> Optional[TRead]:
        """
        Update a document's fields.
        
        Args:
            id_str: The string representation of the document's _id
            update_data: Dictionary of fields to update
            
        Returns:
            Optional[TRead]: The updated document as a Pydantic model, or None if not found
            
        Raises:
            DatabaseException: If there's an error updating the document
        """
        try:
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
        except Exception as e:
            self.logger.error(f"Database error in update: {e}")
            raise DatabaseException(detail=f"Failed to update document: {str(e)}")

    async def delete(self, id_str: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            id_str: The string representation of the document's _id
            
        Returns:
            bool: True if the document was deleted, False otherwise
            
        Raises:
            DatabaseException: If there's an error deleting the document
        """
        try:
            if not ObjectId.is_valid(id_str):
                return False
            result = await self.collection.delete_one({"_id": ObjectId(id_str)})
            if result.deleted_count != 1:
                self.logger.error(f"Delete not acknowledged for id {id_str}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Database error in delete: {e}")
            raise DatabaseException(detail=f"Failed to delete document: {str(e)}")

    async def list(
            self,
            filter_: dict = None,
            projection: dict = None,
            skip: int = 0,
            limit: int = 100,
            sort: List = None
    ) -> List[TRead]:
        """
        List documents matching the filter.
        
        Args:
            filter_: MongoDB query dictionary
            projection: Optional projection dictionary
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: Optional sort specification [field, direction]
            
        Returns:
            List[TRead]: List of documents as Pydantic models
            
        Raises:
            DatabaseException: If there's an error listing documents
        """
        try:
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
        except Exception as e:
            self.logger.error(f"Database error in list: {e}")
            raise DatabaseException(detail=f"Failed to list documents: {str(e)}")

    async def count(self, filter_: dict = None) -> int:
        """
        Count documents matching the filter.
        
        Args:
            filter_: MongoDB query dictionary
            
        Returns:
            int: Number of matching documents
            
        Raises:
            DatabaseException: If there's an error counting documents
        """
        try:
            return await self.collection.count_documents(filter_ or {})
        except Exception as e:
            self.logger.error(f"Database error in count: {e}")
            raise DatabaseException(detail=f"Failed to count documents: {str(e)}")
