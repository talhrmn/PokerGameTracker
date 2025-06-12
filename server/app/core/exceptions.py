import logging
from fastapi import HTTPException, status
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PokerTrackerException(HTTPException):
    """Base exception for all PokerTracker errors."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        logger.error(f"PokerTracker Error: {detail} (Status: {status_code})")


class ResourceNotFoundError(PokerTrackerException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        detail = f"{resource_type} with id {resource_id} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
        logger.warning(f"Resource Not Found: {detail}")


class AccessDeniedError(PokerTrackerException):
    """Raised when a user doesn't have permission to access a resource."""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
        logger.warning(f"Access Denied: {detail}")


class InvalidInputError(PokerTrackerException):
    """Raised when input data is invalid."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
        logger.warning(f"Invalid Input: {detail}")


class GameError(PokerTrackerException):
    """Base exception for game-related errors."""
    pass


class GameStateError(GameError):
    """Raised when a game operation is invalid for the current game state."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
        logger.warning(f"Game State Error: {detail}")


class CashOutError(GameError):
    """Raised when there's an error with cash out operations."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
        logger.warning(f"Cash Out Error: {detail}")


class BuyInError(GameError):
    """Raised when there's an error with buy in operations."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
        logger.warning(f"Buy In Error: {detail}")


class TableError(PokerTrackerException):
    """Base exception for table-related errors."""
    pass


class TableStateError(TableError):
    """Raised when a table operation is invalid for the current table state."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
        logger.warning(f"Table State Error: {detail}")


class DatabaseError(PokerTrackerException):
    """Raised when there's an error with database operations."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}"
        )
        logger.error(f"Database Error: {detail}", exc_info=True)


class ValidationError(PokerTrackerException):
    """Raised when there's a validation error."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
        logger.warning(f"Validation Error: {detail}") 
