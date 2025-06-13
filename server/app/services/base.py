import logging
from typing import Generic, TypeVar, Optional, List

from pydantic import BaseModel

from app.repositories.base import BaseRepository

# TCreate: model type used for creation/insertion
# TRead:   model type used for reading/response
TCreate = TypeVar("TCreate", bound=BaseModel)
TRead = TypeVar("TRead", bound=BaseModel)


class BaseService(Generic[TCreate, TRead]):
    """
    Generic base service wrapping a BaseRepository[TCreate, TRead] for common CRUD operations.
    - TCreate: Pydantic model for create/input (e.g. UserDBInput)
    - TRead:   Pydantic model for read/response (e.g. UserDBResponse)
    """

    def __init__(self, repository: BaseRepository[TCreate, TRead]):
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_by_id(self, id_str: str) -> Optional[TRead]:
        return await self.repository.get_by_id(id_str)

    async def list(
            self,
            filter_: dict = None,
            skip: int = 0,
            limit: int = 100,
            sort: list = None
    ) -> List[TRead]:
        return await self.repository.list(filter_, skip, limit, sort)

    async def create(self, obj_in: TCreate) -> TRead:
        return await self.repository.create(obj_in)

    async def update(self, id_str: str, update_data: dict) -> Optional[TRead]:
        return await self.repository.update(id_str, update_data)

    async def delete(self, id_str: str) -> bool:
        return await self.repository.delete(id_str)
