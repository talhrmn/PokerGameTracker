from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.dependencies import get_database, get_current_user
from app.handlers.games import game_handler
from app.handlers.tables import table_handler
from app.schemas.trends import TrendsResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/", response_model=TrendsResponse)
async def get_trends(current_user: UserResponse = Depends(get_current_user),
                     db_client: AsyncIOMotorClient = Depends(get_database)) -> TrendsResponse:
    games = await game_handler.get_games_for_player(player=current_user, db_client=db_client)
    games.sort(key=lambda game: game.date)
    tables = {game.id: await table_handler.get_table_by_id(table_id=game.table_id, db_client=db_client) for game in
              games}

    pot_data, duration_data, cash_out_data, profit_data, buy_in_data, players_data = {}, {}, {}, {}, {}, {}

    total_pot, total_hours, total_players, average_pot_size, average_win_rate, average_hours_played, \
        average_num_of_players = 0, 0, 0, 0, 0, 0, 0

    wins = 0
    for game in games:
        table_name = tables[game.id].name
        total_pot += game.total_pot
        pot_data[table_name] = game.total_pot
        game_time = game.duration.hours + (game.duration.minutes / 60)
        duration_data[table_name] = game_time
        total_hours += game_time

        game_num_of_players = len(game.players)
        players_data[table_name] = game_num_of_players
        total_players += game_num_of_players

        game_profit = {}
        game_buy_in = {}
        max_player, max_win = "", 0
        for player in game.players:
            game_profit[player.username] = player.net_profit
            if player.net_profit > max_win:
                max_player = player.username
            game_buy_in[player.username] = sum(buyin.amount for buyin in player.buy_ins)

        if max_player == current_user.username:
            wins += 1

        profit_data[table_name] = game_profit
        buy_in_data[table_name] = game_buy_in

    if games:
        num_of_games = len(games)
        average_win_rate = wins / num_of_games
        average_pot_size = total_pot / num_of_games
        average_hours_played = total_hours / num_of_games
        average_num_of_players = total_players / num_of_games

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
