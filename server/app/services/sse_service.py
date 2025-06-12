# app/services/sse_service.py

import asyncio
import json
from dataclasses import dataclass
from typing import Dict, Set

from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.schemas.game import GameDBOutput
from app.schemas.table import TableDBOutput
from app.services.base import BaseService


@dataclass
class States:
    previous: object
    current: object


class SSEService:
    """
    In-memory SSE manager for tables and games.
    """

    def __init__(self, table_service: BaseService, game_service: BaseService):
        self.table_connections: Dict[str, Set[int]] = {}
        self.table_states: Dict[str, States] = {}
        self.game_connections: Dict[str, Set[int]] = {}
        self.game_states: Dict[str, States] = {}

        self.table_service = table_service
        self.game_service = game_service

    async def send_table_update(self, table_id: str, data: TableDBOutput):
        if table_id in self.table_connections:
            if table_id not in self.table_states:
                self.table_states[table_id] = States(previous=None, current=data)
            else:
                self.table_states[table_id].current = data

    async def send_game_update(self, game_id: str, data: GameDBOutput):
        if game_id in self.game_connections:
            if game_id not in self.game_states:
                self.game_states[game_id] = States(previous=None, current=data)
            else:
                self.game_states[game_id].current = data

    async def table_event_stream(self, request: Request, table_id: str) -> StreamingResponse:
        client_id = id(request)
        # Register connection
        if table_id not in self.table_connections:
            self.table_connections[table_id] = set()
        self.table_connections[table_id].add(client_id)

        # Initialize state if first connection
        if table_id not in self.table_states:
            # Fetch initial via TableService
            initial: TableDBOutput = await self.table_service.get_by_id(table_id)
            # Store both previous and current so first yield is initial
            self.table_states[table_id] = States(previous=initial, current=initial)

        async def generate():
            # Send initial state
            state_obj = self.table_states[table_id].current
            try:
                payload = state_obj.model_dump(by_alias=True)
            except Exception:
                payload = state_obj.dict(by_alias=True, exclude_unset=True)
            yield f"data: {json.dumps(payload, default=str)}\n\n"

            try:
                while True:
                    if await request.is_disconnected():
                        break
                    states = self.table_states.get(table_id)
                    if not states:
                        break
                    current = states.current
                    prev = states.previous
                    # If changed (or previous None), send update
                    if prev is None or current != prev:
                        try:
                            payload = current.model_dump(by_alias=True)
                        except Exception:
                            payload = current.dict(by_alias=True, exclude_unset=True)
                        yield f"data: {json.dumps(payload, default=str)}\n\n"
                        states.previous = current
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                pass
            finally:
                # Cleanup connection
                conns = self.table_connections.get(table_id)
                if conns and client_id in conns:
                    conns.remove(client_id)
                    if not conns:
                        del self.table_connections[table_id]
                        if table_id in self.table_states:
                            del self.table_states[table_id]

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    async def game_event_stream(self, request: Request, game_id: str) -> StreamingResponse:
        client_id = id(request)
        if game_id not in self.game_connections:
            self.game_connections[game_id] = set()
        self.game_connections[game_id].add(client_id)

        if game_id not in self.game_states:
            initial: GameDBOutput = await self.game_service.get_by_id(game_id)
            self.game_states[game_id] = States(previous=initial, current=initial)

        async def generate():
            state_obj = self.game_states[game_id].current
            try:
                payload = state_obj.model_dump(by_alias=True)
            except Exception:
                payload = state_obj.dict(by_alias=True, exclude_unset=True)
            yield f"data: {json.dumps(payload, default=str)}\n\n"

            try:
                while True:
                    if await request.is_disconnected():
                        break
                    states = self.game_states.get(game_id)
                    if not states:
                        break
                    current = states.current
                    prev = states.previous
                    if prev is None or current != prev:
                        try:
                            payload = current.model_dump(by_alias=True)
                        except Exception:
                            payload = current.dict(by_alias=True, exclude_unset=True)
                        yield f"data: {json.dumps(payload, default=str)}\n\n"
                        states.previous = current
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                pass
            finally:
                conns = self.game_connections.get(game_id)
                if conns and client_id in conns:
                    conns.remove(client_id)
                    if not conns:
                        del self.game_connections[game_id]
                        if game_id in self.game_states:
                            del self.game_states[game_id]

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
