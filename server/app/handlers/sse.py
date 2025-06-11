import asyncio
import json
from dataclasses import dataclass
from typing import Dict, Set, Generic, TypeVar

from starlette.requests import Request
from starlette.responses import StreamingResponse

from server.app.api.dependencies import get_database
from server.app.handlers.games import game_handler
from server.app.handlers.tables import table_handler
from server.app.schemas.game import GameDBResponse
from server.app.schemas.table import TableDBResponse

T = TypeVar("T")


@dataclass
class States(Generic[T]):
    current: T
    previous: T


@dataclass
class TableData:
    table_connections: Dict[str, Set[int]]
    table_states: Dict[str, States[TableDBResponse]]


@dataclass
class GameData:
    game_connections: Dict[str, Set[int]]
    game_states: Dict[str, States[GameDBResponse]]


class SSEHandler:

    def __init__(self):
        self.table_data = TableData(
            table_connections={},
            table_states={}
        )
        self.game_data = GameData(
            game_connections={},
            game_states={}
        )

    async def send_table_update(self, table_id: str, data: TableDBResponse):
        if table_id in self.table_data.table_connections:
            self.table_data.table_states[table_id].current = data

    async def send_game_update(self, game_id: str, data: GameDBResponse):
        if game_id in self.game_data.game_connections:
            self.game_data.game_states[game_id].current = data

    async def table_event_stream(self, request: Request, table_id: str):
        client_id = id(request)
        if table_id not in self.table_data.table_connections:
            self.table_data.table_connections[table_id] = set()
        self.table_data.table_connections[table_id].add(client_id)

        initial_data = self.table_data.table_states.get(table_id)
        if not initial_data:
            initial_data = await table_handler.get_table_by_id(table_id=table_id, db_client=get_database())
            self.table_data.table_states[table_id] = States(previous=initial_data, current=initial_data)

        async def generate():
            yield f"data: {json.dumps(self.table_data.table_states[table_id].current.model_dump(), default=str)}\n\n"
            try:
                while True:
                    if await request.is_disconnected():
                        break

                    if table_id in self.table_data.table_states:
                        table_states = self.table_data.table_states[table_id]
                        current_state = table_states.current

                        if current_state != table_states.previous:
                            table_states.previous = current_state
                            yield f"data: {json.dumps(current_state.model_dump(), default=str)}\n\n"

                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                pass
            finally:
                if table_id in self.table_data.table_connections and client_id in self.table_data.table_connections[
                    table_id]:
                    self.table_data.table_connections[table_id].remove(client_id)
                    if not self.table_data.table_connections[table_id]:
                        del self.table_data.table_connections[table_id]

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    async def game_event_stream(self, request: Request, game_id: str):
        client_id = id(request)
        if game_id not in self.game_data.game_connections:
            self.game_data.game_connections[game_id] = set()
        self.game_data.game_connections[game_id].add(client_id)

        initial_data = self.game_data.game_states.get(game_id)
        if not initial_data:
            initial_data = await game_handler.get_game_by_id(game_id=game_id, db_client=get_database())
            self.game_data.game_states[game_id] = States(previous=initial_data, current=initial_data)

        async def generate():
            yield f"data: {json.dumps(self.game_data.game_states[game_id].current.model_dump(), default=str)}\n\n"

            try:
                while True:
                    if await request.is_disconnected():
                        break

                    if game_id in self.game_data.game_states:
                        game_states = self.game_data.game_states[game_id]
                        current_state = game_states.current

                        if current_state != game_states.previous:
                            game_states.previous = current_state
                            yield f"data: {json.dumps(current_state.model_dump(), default=str)}\n\n"

                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                pass
            finally:
                if game_id in self.game_data.game_connections and client_id in self.game_data.game_connections[game_id]:
                    self.game_data.game_connections[game_id].remove(client_id)
                    if not self.game_data.game_connections[game_id]:
                        del self.game_data.game_connections[game_id]

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )


sse_handler = SSEHandler()
