from fastapi import APIRouter
from starlette.requests import Request

from app.handlers.sse import sse_handler

router = APIRouter()


@router.get("/tables/{table_id}")
async def table_events(request: Request, table_id: str):
    return await sse_handler.table_event_stream(request, table_id)


@router.get("/games/{game_id}")
async def game_events(request: Request, game_id: str):
    return await sse_handler.game_event_stream(request, game_id)
