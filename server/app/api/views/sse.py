from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.api.dependencies import get_sse_service
from app.core.exceptions import ValidationException
from app.services.sse_service import SSEService

router = APIRouter()


@router.get("/tables/{table_id}")
async def table_events(
        request: Request,
        table_id: str,
        sse_service: SSEService = Depends(get_sse_service)
) -> StreamingResponse:
    """
    Stream server-sent events for a specific table.
    
    Args:
        request: The incoming request
        table_id: ID of the table to stream events for
        sse_service: The SSE service
        
    Returns:
        A streaming response with table events
        
    Raises:
        ValidationException: If the table ID is invalid
    """
    if not table_id:
        raise ValidationException(detail="Table ID is required")

    return await sse_service.table_event_stream(request, table_id)


@router.get("/games/{game_id}")
async def game_events(
        request: Request,
        game_id: str,
        sse_service: SSEService = Depends(get_sse_service)
) -> StreamingResponse:
    """
    Stream server-sent events for a specific game.
    
    Args:
        request: The incoming request
        game_id: ID of the game to stream events for
        sse_service: The SSE service
        
    Returns:
        A streaming response with game events
        
    Raises:
        ValidationException: If the game ID is invalid
    """
    if not game_id:
        raise ValidationException(detail="Game ID is required")

    return await sse_service.game_event_stream(request, game_id)
