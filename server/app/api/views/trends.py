from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_game_service, get_table_service
from app.schemas.trends import TrendsResponse
from app.schemas.user import UserResponse
from app.services.game_service import GameService
from app.services.table_service import TableService

router = APIRouter()


@router.get("/", response_model=TrendsResponse)
async def get_trends(
        current_user: UserResponse = Depends(get_current_user),
        table_service: TableService = Depends(get_table_service),
        game_service: GameService = Depends(get_game_service)
) -> TrendsResponse:
    """
    Get trend statistics for the current user's games.
    
    Args:
        current_user: The current authenticated user
        table_service: The table service
        game_service: The game service
        
    Returns:
        Trend statistics including:
        - Average pot size
        - Average win rate
        - Average hours played
        - Average number of players
        - Pot trends
        - Player count trends
        - Duration trends
        - Profit trends
        - Buy-in trends
        
    Raises:
        DatabaseException: If any database operation fails
    """
    games = await game_service.get_games_for_player(current_user)
    games.sort(key=lambda game: game.date)
    tables = {game.id: await table_service.get_by_id(str(game.table_id)) for game in games}

    # Initialize trend data dictionaries
    pot_data = {}
    duration_data = {}
    cash_out_data = {}
    profit_data = {}
    buy_in_data = {}
    players_data = {}

    # Initialize totals
    total_pot = 0
    total_hours = 0
    total_players = 0
    wins = 0

    # Calculate trends for each game
    for game in games:
        table_name = tables[game.id].name

        # Update pot statistics
        total_pot += game.total_pot
        pot_data[table_name] = game.total_pot

        # Update duration statistics
        game_time = game.duration.hours + (game.duration.minutes / 60)
        duration_data[table_name] = game_time
        total_hours += game_time

        # Update player statistics
        game_num_of_players = len(game.players)
        players_data[table_name] = game_num_of_players
        total_players += game_num_of_players

        # Calculate profit and buy-in data
        game_profit = {}
        game_buy_in = {}
        max_player = ""
        max_win = 0

        for player in game.players:
            game_profit[player.username] = player.net_profit
            if player.net_profit > max_win:
                max_player = player.username
                max_win = player.net_profit
            game_buy_in[player.username] = sum(buyin.amount for buyin in player.buy_ins)

        if max_player == current_user.username:
            wins += 1

        profit_data[table_name] = game_profit
        buy_in_data[table_name] = game_buy_in

    num_of_games = len(games)
    average_win_rate = wins / num_of_games if num_of_games > 0 else 0
    average_pot_size = total_pot / num_of_games if num_of_games > 0 else 0
    average_hours_played = total_hours / num_of_games if num_of_games > 0 else 0
    average_num_of_players = total_players / num_of_games if num_of_games > 0 else 0

    return TrendsResponse(
        average_pot_size=average_pot_size,
        average_win_rate=average_win_rate,
        average_hours_played=average_hours_played,
        average_num_of_players=average_num_of_players,
        pot_trend=pot_data,
        players_trend=players_data,
        duration_trend=duration_data,
        profit_trend=profit_data,
        buy_in_trend=buy_in_data
    )
