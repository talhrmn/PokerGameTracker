from app.core.exceptions import DatabaseError
from app.schemas.trends import TrendsResponse
from app.schemas.user import UserResponse
from app.services.game import GameService
from app.services.table import TableService


class TrendsService:
    def __init__(self, game_service: GameService, table_service: TableService):
        """Initialize the trends service with required dependencies."""
        self.game_service = game_service
        self.table_service = table_service

    async def get_trends(self, current_user: UserResponse) -> TrendsResponse:
        """Get trends data for the current user."""
        try:
            # Get all games for the player
            games = await self.game_service.get_games_for_player(current_user)
            games.sort(key=lambda game: game.date)

            # Get tables for each game
            tables = {
                game.id: await self.table_service.get_table_by_id(game.table_id)
                for game in games
            }

            # Initialize data structures
            (
                pot_data,
                duration_data,
                cash_out_data,
                profit_data,
                buy_in_data,
                players_data,
            ) = ({}, {}, {}, {}, {}, {})
            total_pot, total_hours, total_players = 0, 0, 0
            wins = 0

            # Process each game
            for game in games:
                table = tables[game.id]
                table_name = table.name

                # Update totals
                total_pot += game.total_pot
                pot_data[table_name] = game.total_pot

                # Calculate game duration
                game_time = game.duration.hours + (game.duration.minutes / 60)
                duration_data[table_name] = game_time
                total_hours += game_time

                # Process players
                game_num_of_players = len(game.players)
                players_data[table_name] = game_num_of_players
                total_players += game_num_of_players

                # Process profits and buy-ins
                game_profit = {}
                game_buy_in = {}
                max_player, max_win = "", 0

                for player in game.players:
                    game_profit[player.username] = player.net_profit
                    if player.net_profit > max_win:
                        max_player = player.username
                    game_buy_in[player.username] = sum(
                        buyin.amount for buyin in player.buy_ins
                    )

                if max_player == current_user.username:
                    wins += 1

                profit_data[table_name] = game_profit
                buy_in_data[table_name] = game_buy_in

            # Calculate averages
            num_of_games = len(games)
            average_win_rate = wins / num_of_games if num_of_games > 0 else 0
            average_pot_size = total_pot / num_of_games if num_of_games > 0 else 0
            average_hours_played = total_hours / num_of_games if num_of_games > 0 else 0
            average_num_of_players = (
                total_players / num_of_games if num_of_games > 0 else 0
            )

            return TrendsResponse(
                average_pot_size=average_pot_size,
                average_win_rate=average_win_rate,
                average_hours_played=average_hours_played,
                average_num_of_players=average_num_of_players,
                pot_trend=pot_data,
                players_trend=players_data,
                duration_trend=duration_data,
                profit_trend=profit_data,
                buy_in_trend=buy_in_data,
            )
        except Exception as e:
            raise DatabaseError(f"Failed to get trends: {str(e)}")
