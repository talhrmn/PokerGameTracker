from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_sse_service, get_table_service, get_game_service, \
    get_statistics_service
from app.core.exceptions import ValidationException, NotFoundException, PermissionDeniedException
from app.schemas.game import GameUpdate, GameDBInput, GameBase, GameStatusEnum, GameDBOutput, BuyIn, CashOut, Duration
from app.schemas.statistics import Stats, MonthlyStats
from app.schemas.user import UserResponse
from app.services.game_service import GameService
from app.services.sse_service import SSEService
from app.services.statistics_service import StatisticsService
from app.services.table_service import TableService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GameDBOutput)
async def create_game(
        game: GameBase,
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service),
        game_service: GameService = Depends(get_game_service)
) -> GameDBOutput:
    """
    Create a new game.
    
    Args:
        game: Game data
        current_user: The current authenticated user
        table_service: The table service
        game_service: The game service
        
    Returns:
        The created game
    """
    table = await table_service.get_by_id(str(game.table_id))
    if not table:
        raise NotFoundException(detail="Table not found")

    if str(table.creator_id) != str(current_user.id):
        raise PermissionDeniedException(detail="Only table creator can start a game")

    game = await game_service.create_game(game, current_user)
    updated_data = {"game_id": str(game.id), "status": GameStatusEnum.IN_PROGRESS}
    await table_service.update_table(str(game.table_id), updated_data)
    return game


@router.get("/", response_model=List[GameDBOutput])
async def get_games(
        table_id: str = None,
        status: str = None,
        limit: int = None,
        skip: int = None,
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service)
) -> List[GameDBOutput]:
    """
    Get games for the current user.
    
    Args:
        table_id: Optional table ID to filter by
        status: Optional status to filter by
        limit: Optional limit for pagination
        skip: Optional skip for pagination
        current_user: The current authenticated user
        game_service: The game service
        
    Returns:
        List of games
    """
    return await game_service.get_games_for_player(current_user, table_id, status, skip, limit)


@router.get("/count", response_model=int)
async def get_games_count(
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service)
) -> int:
    """
    Get count of games for the current user.
    
    Args:
        current_user: The current authenticated user
        game_service: The game service
        
    Returns:
        Number of games
    """
    return await game_service.count_games_for_player(current_user)


@router.get("/{game_id}", response_model=GameDBInput)
async def get_game(
        game_id: str,
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service)
) -> GameDBOutput:
    """
    Get a specific game.
    
    Args:
        game_id: ID of the game
        current_user: The current authenticated user
        game_service: The game service
        
    Returns:
        The game data
    """
    if not ObjectId.is_valid(game_id):
        raise ValidationException(detail="Invalid game ID")

    game = await game_service.get_by_id(game_id)
    if not game:
        raise NotFoundException(detail="Game not found")

    user_is_player = any(str(player.user_id) == str(current_user.id) for player in game.players)
    user_is_game_creator = str(game.creator_id) == str(current_user.id)

    if not (user_is_player or user_is_game_creator):
        raise PermissionDeniedException(detail="Access denied")

    return game


@router.put("/{game_id}", response_model=Optional[GameDBOutput])
async def update_game(
        game_id: str,
        game_update: GameUpdate,
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service),
        table_service: TableService = Depends(get_table_service),
        statistics_service: StatisticsService = Depends(get_statistics_service),
        sse_service: SSEService = Depends(get_sse_service)
) -> GameDBOutput:
    """
    Update a game.
    
    Args:
        game_id: ID of the game
        game_update: Updated game data
        current_user: The current authenticated user
        game_service: The game service
        table_service: The table service
        statistics_service: The statistics service
        sse_service: The SSE service
        
    Returns:
        The updated game
    """
    if not ObjectId.is_valid(game_id):
        raise ValidationException(detail="Invalid game ID")

    game = await game_service.get_by_id(game_id)
    if not game:
        raise NotFoundException(detail="Game not found")

    table = await table_service.get_by_id(str(game.table_id))
    if not table or str(table.creator_id) != str(current_user.id):
        raise PermissionDeniedException(detail="Only the table creator can modify the game")

    updated = await game_service.update_game(game_id, game_update)

    is_completing = (game_update.status == GameStatusEnum.COMPLETED)
    was_not_completed = (game.status != GameStatusEnum.COMPLETED)
    if is_completing and was_not_completed:
        await table_service.update_table(str(game.table_id), {"status": GameStatusEnum.COMPLETED.value})

        for player in game.players:
            user_id = str(player.user_id)
            profit = player.net_profit
            duration = game.duration or Duration()
            hours_played = duration.hours + (duration.minutes / 60)

            won = 1 if profit > 0 else 0
            loss = 1 if profit <= 0 else 0

            user_stats = Stats(total_profit=profit, games_won=won, games_lost=loss, tables_played=1,
                               hours_played=hours_played)
            await statistics_service.update_user_stats(user_id, user_stats)

            month_str = game.date.strftime("%b %Y")
            user_monthly = MonthlyStats(
                month=month_str,
                profit=profit,
                games_won=won,
                games_lost=loss,
                tables_played=1,
                hours_played=hours_played
            )
            await statistics_service.update_user_monthly_stats(user_id, month_str, user_monthly)

            # win_rate = await game_service.get_user_win_rate(user_id)
            # if win_rate:
            #     await statistics_service.update_win_rate(user_id, win_rate)
            #
            # monthly_rates = await game_service.get_user_monthly_win_rates(user_id)
            # if monthly_rates:
            #     await statistics_service.update_monthly_win_rates(user_id, monthly_rates)

    try:
        await sse_service.send_game_update(game_id=game_id, data=updated)
    except Exception:
        pass  # SSE errors are not critical

    return updated


@router.put("/{game_id}/buyin", response_model=Optional[GameDBOutput])
async def update_player_buyin(
        game_id: str,
        buyin: BuyIn,
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service),
        sse_service: SSEService = Depends(get_sse_service)
) -> GameDBOutput:
    """
    Update player's buy-in for a game.
    
    Args:
        game_id: ID of the game
        buyin: Buy-in data
        current_user: The current authenticated user
        game_service: The game service
        sse_service: The SSE service
        
    Returns:
        The updated game
    """
    if not ObjectId.is_valid(game_id):
        raise ValidationException(detail="Invalid game ID")

    game = await game_service.get_by_id(game_id)
    if not game:
        raise NotFoundException(detail="Game not found")

    updated_game = await game_service.update_player_buyin(game_id, current_user, buyin)

    try:
        await sse_service.send_game_update(game_id=game_id, data=updated_game)
    except Exception:
        pass  # SSE errors are not critical

    return updated_game


@router.put("/{game_id}/cashout", response_model=Optional[GameDBOutput])
async def update_player_cashout(
        game_id: str,
        cash_out: CashOut,
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service),
        sse_service: SSEService = Depends(get_sse_service)
) -> GameDBOutput:
    """
    Update player's cash-out for a game.
    
    Args:
        game_id: ID of the game
        cash_out: Cash-out data
        current_user: The current authenticated user
        game_service: The game service
        sse_service: The SSE service
        
    Returns:
        The updated game
    """
    if not ObjectId.is_valid(game_id):
        raise ValidationException(detail="Invalid game ID")

    game = await game_service.get_by_id(game_id)
    if not game:
        raise NotFoundException(detail="Game not found")

    updated_game = await game_service.update_player_cashout(game_id, current_user, cash_out)

    try:
        await sse_service.send_game_update(game_id=game_id, data=updated_game)
    except Exception:
        pass  # SSE errors are not critical

    return updated_game


@router.post("/{game_id}/end", response_model=Optional[GameDBOutput])
async def update_end_game(
        game_id: str,
        current_user: UserResponse = Depends(get_current_user),
        game_service: GameService = Depends(get_game_service),
        table_service: TableService = Depends(get_table_service),
        statistics_service: StatisticsService = Depends(get_statistics_service),
        sse_service: SSEService = Depends(get_sse_service)
) -> GameDBOutput:
    """
    End a game.
    
    Args:
        game_id: ID of the game
        current_user: The current authenticated user
        game_service: The game service
        table_service: The table service
        statistics_service: The statistics service
        sse_service: The SSE service
        
    Returns:
        The updated game
    """
    if not ObjectId.is_valid(game_id):
        raise ValidationException(detail="Invalid game ID")

    game = await game_service.get_by_id(game_id)
    if not game:
        raise NotFoundException(detail="Game not found")

    if str(game.creator_id) != str(current_user.id):
        raise PermissionDeniedException(detail="Only game creator can end the game")

    updated_game = await game_service.end_game(game_id)
    await table_service.update_table(str(updated_game.table_id), {"status": GameStatusEnum.COMPLETED})

    for player in game.players:
        user_id = str(player.user_id)
        profit = player.net_profit
        duration = game.duration or Duration()
        hours_played = duration.hours + (duration.minutes / 60)

        won = 1 if profit > 0 else 0
        loss = 1 if profit <= 0 else 0

        user_stats = Stats(total_profit=profit, games_won=won, games_lost=loss, tables_played=1,
                           hours_played=hours_played)
        await statistics_service.update_user_stats(user_id, user_stats)

        month_str = game.date.strftime("%b %Y")
        user_monthly = MonthlyStats(
            month=month_str,
            profit=profit,
            games_won=won,
            games_lost=loss,
            tables_played=1,
            hours_played=hours_played
        )
        await statistics_service.update_user_monthly_stats(user_id, month_str, user_monthly)

    try:
        await sse_service.send_game_update(game_id=game_id, data=updated_game)
    except Exception:
        pass  # SSE errors are not critical

    return updated_game
