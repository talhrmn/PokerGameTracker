import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, Set

from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.core.exceptions import (
    NotFoundException,
    StreamException
)
from app.schemas.game import GameDBOutput
from app.schemas.table import TableDBOutput
from app.services.base import BaseService


@dataclass
class States:
    """
    Data class to track state changes for SSE streams.
    
    Attributes:
        previous: The previous state of the object
        current: The current state of the object
    """
    previous: object
    current: object


class SSEService:
    """
    Service for managing Server-Sent Events (SSE) for tables and games.
    
    This service handles real-time updates for tables and games using SSE:
    - Manages client connections and disconnections
    - Tracks state changes for tables and games
    - Sends updates to connected clients
    - Handles cleanup of disconnected clients
    
    Attributes:
        table_connections: Dictionary mapping table IDs to sets of client IDs
        table_states: Dictionary mapping table IDs to their state objects
        game_connections: Dictionary mapping game IDs to sets of client IDs
        game_states: Dictionary mapping game IDs to their state objects
    """

    def __init__(self, table_service: BaseService, game_service: BaseService):
        """
        Initialize the SSE service.
        
        Args:
            table_service: Service for table operations
            game_service: Service for game operations
        """
        self.table_connections: Dict[str, Set[int]] = {}
        self.table_states: Dict[str, States] = {}
        self.game_connections: Dict[str, Set[int]] = {}
        self.game_states: Dict[str, States] = {}

        self.table_service = table_service
        self.game_service = game_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_table_update(self, table_id: str, data: TableDBOutput) -> None:
        """
        Update the state for a table and prepare for SSE broadcast.
        
        Args:
            table_id: The ID of the table to update
            data: The new table data
            
        Raises:
            StreamException: If there's an error updating the table state
        """
        try:
            if table_id in self.table_connections:
                if table_id not in self.table_states:
                    self.table_states[table_id] = States(previous=None, current=data)
                else:
                    self.table_states[table_id].current = data
        except Exception as e:
            self.logger.error(f"Error sending table update: {e}")
            raise StreamException(detail="Failed to send table update")

    async def send_game_update(self, game_id: str, data: GameDBOutput) -> None:
        """
        Update the state for a game and prepare for SSE broadcast.
        
        Args:
            game_id: The ID of the game to update
            data: The new game data
            
        Raises:
            StreamException: If there's an error updating the game state
        """
        try:
            if game_id in self.game_connections:
                if game_id not in self.game_states:
                    self.game_states[game_id] = States(previous=None, current=data)
                else:
                    self.game_states[game_id].current = data
        except Exception as e:
            self.logger.error(f"Error sending game update: {e}")
            raise StreamException(detail="Failed to send game update")

    async def table_event_stream(self, request: Request, table_id: str) -> StreamingResponse:
        """
        Create an SSE stream for table updates.
        
        Args:
            request: The client request
            table_id: The ID of the table to stream
            
        Returns:
            StreamingResponse: The SSE stream response
            
        Raises:
            NotFoundException: If table not found
            StreamException: If there's an error creating the stream
        """
        try:
            client_id = id(request)
            # Register connection
            if table_id not in self.table_connections:
                self.table_connections[table_id] = set()
            self.table_connections[table_id].add(client_id)

            # Initialize state if first connection
            if table_id not in self.table_states:
                # Fetch initial via TableService
                initial: TableDBOutput = await self.table_service.get_by_id(table_id)
                if not initial:
                    raise NotFoundException(detail="Table not found")
                # Store both previous and current so first yield is initial
                self.table_states[table_id] = States(previous=initial, current=initial)

            async def generate():
                try:
                    # Send initial state
                    state_obj = self.table_states[table_id].current
                    try:
                        payload = state_obj.model_dump(by_alias=True)
                    except Exception:
                        payload = state_obj.dict(by_alias=True, exclude_unset=True)
                    yield f"data: {json.dumps(payload, default=str)}\n\n"

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
                except Exception as e:
                    self.logger.error(f"Error in table event stream: {e}")
                    raise StreamException(detail="Error in table event stream")
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
        except NotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating table event stream: {e}")
            raise StreamException(detail="Failed to create table event stream")

    async def game_event_stream(self, request: Request, game_id: str) -> StreamingResponse:
        """
        Create an SSE stream for game updates.
        
        Args:
            request: The client request
            game_id: The ID of the game to stream
            
        Returns:
            StreamingResponse: The SSE stream response
            
        Raises:
            NotFoundException: If game not found
            StreamException: If there's an error creating the stream
        """
        try:
            client_id = id(request)
            if game_id not in self.game_connections:
                self.game_connections[game_id] = set()
            self.game_connections[game_id].add(client_id)

            if game_id not in self.game_states:
                initial: GameDBOutput = await self.game_service.get_by_id(game_id)
                if not initial:
                    raise NotFoundException(detail="Game not found")
                self.game_states[game_id] = States(previous=initial, current=initial)

            async def generate():
                try:
                    state_obj = self.game_states[game_id].current
                    try:
                        payload = state_obj.model_dump(by_alias=True)
                    except Exception:
                        payload = state_obj.dict(by_alias=True, exclude_unset=True)
                    yield f"data: {json.dumps(payload, default=str)}\n\n"

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
                except Exception as e:
                    self.logger.error(f"Error in game event stream: {e}")
                    raise StreamException(detail="Error in game event stream")
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
        except NotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating game event stream: {e}")
            raise StreamException(detail="Failed to create game event stream")
