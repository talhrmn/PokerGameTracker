from datetime import UTC, datetime
from typing import List, Optional

from app.api.dependencies import (
    get_current_user,
    get_game_service,
    get_sse_service,
    get_table_service,
)
from app.core.exceptions import DatabaseError, InvalidInputError, ResourceNotFoundError
from app.schemas.game import (
    BuyIn,
    CashOut,
    Duration,
    GameCreate,
    GameDBResponse,
    GameStatusEnum,
    GameUpdate,
    PlayerStatusEnum,
)
from app.schemas.user import UserResponse
from app.services.game import GameService
from app.services.sse import SSEService
from app.services.table import TableService
from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post("/", response_model=GameDBResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    table_service: TableService = Depends(get_table_service),
    sse_service: SSEService = Depends(get_sse_service),
):
    """Create a new game."""
    try:
        # Create the game
        created_game = await game_service.create_game(game_data, current_user)

        # Update table status
        await table_service.update_table(
            game_data.table_id,
            {
                "game_id": str(created_game.id),
                "status": GameStatusEnum.IN_PROGRESS.value,
            },
        )

        # Send SSE update
        try:
            await sse_service.send_game_update(
                game_id=str(created_game.id), data=created_game
            )
        except:
            pass

        return created_game
    except Exception as e:
        raise DatabaseError(f"Failed to create game: {str(e)}")


@router.get("/", response_model=List[GameDBResponse])
async def get_games(
    table_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
):
    """Get all games for the current user."""
    try:
        return await game_service.get_games_for_player(
            current_user, table_id, status, skip, limit
        )
    except Exception as e:
        raise DatabaseError(f"Failed to get games: {str(e)}")


@router.get("/{game_id}", response_model=GameDBResponse)
async def get_game(
    game_id: str,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
):
    """Get a specific game."""
    try:
        game = await game_service.get_game_by_id(game_id)
        if not game:
            raise ResourceNotFoundError(f"Game {game_id} not found")

        # Check if user is a player or creator
        if (
            str(current_user.id) not in [p.user_id for p in game.players]
            and str(current_user.id) != game.creator_id
        ):
            raise InvalidInputError("You don't have access to this game")

        return game
    except Exception as e:
        raise DatabaseError(f"Failed to get game: {str(e)}")


@router.put("/{game_id}", response_model=GameDBResponse)
async def update_game(
    game_id: str,
    game_data: GameUpdate,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    sse_service: SSEService = Depends(get_sse_service),
):
    """Update a game."""
    try:
        game = await game_service.get_game_by_id(game_id)
        if not game:
            raise ResourceNotFoundError("Game not found")
        if game.creator_id != str(current_user.id):
            raise InvalidInputError("Only the creator can modify the game")
        await game_service.update_game(
            game_id, game_data.model_dump(exclude_unset=True)
        )
        updated_game = await game_service.get_game_by_id(game_id)
        try:
            await sse_service.send_game_update(game_id=game_id, data=updated_game)
        except:
            pass
        return updated_game
    except Exception as e:
        raise DatabaseError(f"Failed to update game: {str(e)}")


@router.put("/{game_id}/invite", response_model=GameDBResponse)
async def respond_to_invite(
    game_id: str,
    status: PlayerStatusEnum,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    sse_service: SSEService = Depends(get_sse_service),
):
    """Respond to a game invite."""
    try:
        game = await game_service.get_game_by_id(game_id)
        if not game:
            raise ResourceNotFoundError("Game not found")
        user_is_invited = any(
            player.user_id == str(current_user.id)
            and player.status == PlayerStatusEnum.INVITED
            for player in game.players
        )
        if not user_is_invited:
            raise InvalidInputError("You are not invited to this game")
        await game_service.update_game_invite(game_id, current_user, status)
        updated_game = await game_service.get_game_by_id(game_id)
        try:
            await sse_service.send_game_update(game_id=game_id, data=updated_game)
        except:
            pass
        return updated_game
    except Exception as e:
        raise DatabaseError(f"Failed to respond to invite: {str(e)}")


@router.put("/{game_id}/buyin", response_model=GameDBResponse)
async def update_buyin(
    game_id: str,
    buyin: BuyIn,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    sse_service: SSEService = Depends(get_sse_service),
):
    """Update player buyin."""
    try:
        game = await game_service.get_game_by_id(game_id)
        if not game:
            raise ResourceNotFoundError("Game not found")

        # Check if user is a player
        current_player = [
            player for player in game.players if player.user_id == str(current_user.id)
        ]
        if not current_player:
            raise InvalidInputError("You are not a player in this game")

        # Get current game state
        current_pot = game.total_pot
        current_available_cash_out = game.available_cash_out

        await game_service.update_player_buyin(
            game_id,
            str(current_user.id),
            buyin,
            current_pot,
            current_available_cash_out,
        )
        updated_game = await game_service.get_game_by_id(game_id)
        try:
            await sse_service.send_game_update(game_id=game_id, data=updated_game)
        except:
            pass
        return updated_game
    except Exception as e:
        raise DatabaseError(f"Failed to update buyin: {str(e)}")


@router.put("/{game_id}/cashout", response_model=GameDBResponse)
async def update_cashout(
    game_id: str,
    cash_out: CashOut,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    sse_service: SSEService = Depends(get_sse_service),
):
    """Update player cashout."""
    try:
        game = await game_service.get_game_by_id(game_id)
        if not game:
            raise ResourceNotFoundError("Game not found")

        # Check if user is a player
        current_player = [
            player for player in game.players if player.user_id == str(current_user.id)
        ]
        if not current_player:
            raise InvalidInputError("You are not a player in this game")

        # Validate cashout amount against available cash
        if cash_out.amount > game.available_cash_out:
            raise InvalidInputError("Invalid cash out amount")

        # Calculate total buy-ins for the player
        total_buy_ins = sum(buy_in.amount for buy_in in current_player[0].buy_ins)

        # Calculate new cashout and net profit
        new_cashout = cash_out.amount + current_player[0].cash_out
        net_profit = cash_out.amount - total_buy_ins

        await game_service.update_player_cashout(
            game_id,
            str(current_user.id),
            new_cashout,
            net_profit,
            game.available_cash_out,
        )
        updated_game = await game_service.get_game_by_id(game_id)
        try:
            await sse_service.send_game_update(game_id=game_id, data=updated_game)
        except:
            pass
        return updated_game
    except Exception as e:
        raise DatabaseError(f"Failed to update cashout: {str(e)}")


@router.post("/{game_id}/end", response_model=GameDBResponse)
async def update_end_game(
    game_id: str,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    sse_service: SSEService = Depends(get_sse_service),
):
    """End a game."""
    try:
        game = await game_service.get_game_by_id(game_id)
        if not game:
            raise ResourceNotFoundError("Game not found")

        # Check if user is the creator
        if str(game.creator_id) != str(current_user.id):
            raise InvalidInputError("Only game creator can end the game")

        # Validate that all cashouts match buyins
        if (
            game.available_cash_out != 0
            or sum(player.cash_out for player in game.players) != game.total_pot
        ):
            raise InvalidInputError("Cashout doesn't match buyins")

        # Calculate game duration
        time_diff = datetime.now(UTC) - game.created_at
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        # Prepare update data
        update_data = {
            "status": GameStatusEnum.COMPLETED.value,
            "duration": Duration(hours=int(hours), minutes=int(minutes)).model_dump(),
        }

        await game_service.update_game(game_id, update_data)
        updated_game = await game_service.get_game_by_id(game_id)
        try:
            await sse_service.send_game_update(game_id=game_id, data=updated_game)
        except:
            pass
        return updated_game
    except Exception as e:
        raise DatabaseError(f"Failed to end game: {str(e)}")


@router.get("/recent/{limit}", response_model=List[GameDBResponse])
async def get_recent_games(
    limit: int,
    current_user: UserResponse = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
):
    """Get recent games for the current user."""
    try:
        return await game_service.get_recent_games(str(current_user.id), limit)
    except Exception as e:
        raise DatabaseError(f"Failed to get recent games: {str(e)}")
