from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.api.dependencies import get_sse_service

router = APIRouter()


@router.get("/tables/{table_id}")
async def table_events(
        request: Request,
        table_id: str,
        sse_service=Depends(get_sse_service)
):
    return await sse_service.table_event_stream(request, table_id)


@router.get("/games/{game_id}")
async def game_events(
        request: Request,
        game_id: str,
        sse_service=Depends(get_sse_service)
):
    return await sse_service.game_event_stream(request, game_id)
