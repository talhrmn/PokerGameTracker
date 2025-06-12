from typing import Generic, TypeVar

from app.repositories.base import BaseRepository

T = TypeVar("T")
R = TypeVar("R", bound=BaseRepository)


class BaseService(Generic[T, R]):
    def __init__(self, repository: R):
        self.repository = repository
