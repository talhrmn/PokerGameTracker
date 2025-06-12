from app.api.dependencies import get_sse_service
from app.services.sse import SSEService
from fastapi import APIRouter, Depends, Request
from starlette.responses import StreamingResponse

router = APIRouter()


@router.get("/table/{table_id}")
async def table_event_stream(
    request: Request,
    table_id: str,
    sse_service: SSEService = Depends(get_sse_service),
) -> StreamingResponse:
    """Create SSE stream for table updates."""
    return await sse_service.table_event_stream(request, table_id)


@router.get("/game/{game_id}")
async def game_event_stream(
    request: Request,
    game_id: str,
    sse_service: SSEService = Depends(get_sse_service),
) -> StreamingResponse:
    """Create SSE stream for game updates."""
    return await sse_service.game_event_stream(request, game_id)
