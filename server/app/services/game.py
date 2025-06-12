import logging
from typing import Dict, List, Optional

from app.core.exceptions import (
    DatabaseError,
    GameStateError,
    InvalidInputError,
    ResourceNotFoundError,
)
from app.db.mongo_client import AsyncIOMotorClient
from app.repositories.game import GameRepository
from app.repositories.table import TableRepository
from app.repositories.user import UserRepository
from app.schemas.game import (
    BuyIn,
    Duration,
    GameBase,
    GameDBResponse,
    GameStatusEnum,
    GameUpdate,
)
from app.schemas.table import PlayerStatusEnum
from app.schemas.user import MonthlyStats, UserDBResponse, UserResponse, UserStats
from app.services.base import BaseService

# Configure logger
logger = logging.getLogger(__name__)


class GameService(BaseService):
    def __init__(
        self,
        db_client: AsyncIOMotorClient,
        table_repository: TableRepository,
        user_repository: UserRepository,
    ):
        """Initialize the game service with required dependencies."""
        super().__init__(GameRepository(db_client))
        self.table_repository = table_repository
        self.user_repository = user_repository

    async def get_game_by_id(self, game_id: str) -> Optional[GameDBResponse]:
        """Get a game by ID."""
        try:
            return await self.repository.get_game_by_id(game_id)
        except Exception as e:
            logger.error(f"Failed to get game {game_id}: {str(e)}")
            raise DatabaseError(f"Failed to get game: {str(e)}")

    async def create_game(
        self, game: GameBase, user: UserResponse
    ) -> GameDBResponse:
        """Create a new game."""
        try:
            # Validate table exists and user is creator
            table = await self.table_repository.get_by_id(game.table_id)
            if not table:
                raise ResourceNotFoundError("Table not found")

            # Validate user is table creator
            if str(table.created_by) != str(user.id):
                raise InvalidInputError("Only table creator can create games")

            # Create game
            game_id = await self.repository.create_game(game, user)
            created_game = await self.repository.get_game_by_id(str(game_id))

            # Update table with game info
            await self.table_repository.update_table(
                game.table_id,
                {"game_id": str(created_game.id), "status": GameStatusEnum.IN_PROGRESS},
            )

            return created_game
        except Exception as e:
            raise DatabaseError(f"Failed to create game: {str(e)}")

    async def update_game_invite(
        self, game_id: str, user: UserResponse, status: PlayerStatusEnum
    ) -> None:
        try:
            await self.repository.update_game_invite(game_id, user, status)
        except Exception as e:
            logger.error(
                f"Failed to update game invite for game {game_id} and user {user.id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to update game invite: {str(e)}")

    async def update_player_buyin(
        self,
        game_id: str,
        player_id: str,
        buyin: BuyIn,
        total_pot: float,
        available_cash_out: float,
    ) -> None:
        try:
            await self.repository.update_player_buyin(
                game_id, player_id, buyin, total_pot, available_cash_out
            )
        except Exception as e:
            logger.error(
                f"Failed to update player buyin for game {game_id} and player {player_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to update player buyin: {str(e)}")

    async def update_player_cashout(
        self,
        game_id: str,
        player_id: str,
        cashout: float,
        net_profit: float,
        available_cash_out: float,
    ) -> None:
        try:
            await self.repository.update_player_cashout(
                game_id, player_id, cashout, net_profit, available_cash_out
            )
        except Exception as e:
            logger.error(
                f"Failed to update player cashout for game {game_id} and player {player_id}: {str(e)}"
            )
            raise DatabaseError(f"Failed to update player cashout: {str(e)}")

    async def get_games_for_player(
        self,
        player: UserResponse,
        table_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[GameDBResponse]:
        try:
            return await self.repository.get_games_for_player(
                player, table_id, status, skip, limit
            )
        except Exception as e:
            logger.error(f"Failed to get games for player {player.id}: {str(e)}")
            raise DatabaseError(f"Failed to get games: {str(e)}")

    async def get_games_count_for_player(self, player: UserResponse) -> int:
        try:
            return await self.repository.get_games_count_for_player(player)
        except Exception as e:
            logger.error(f"Failed to get games count for player {player.id}: {str(e)}")
            raise DatabaseError(f"Failed to get games count: {str(e)}")

    async def update_game(
        self, game_id: str, game_update: GameUpdate, user: UserDBResponse
    ) -> GameDBResponse:
        """Update a game."""
        try:
            game = await self.repository.get_game_by_id(game_id)
            if not game:
                raise ResourceNotFoundError("Game not found")

            # Validate user is game creator
            if str(game.created_by) != str(user.id):
                raise InvalidInputError("Only game creator can update game")

            # Update game
            await self.repository.update_game(game_id, game_update.model_dump(exclude_unset=True))
            updated_game = await self.repository.get_game_by_id(game_id)

            # If game is completed, update table status and stats
            if (
                game_update.status == GameStatusEnum.COMPLETED
                and game.status != GameStatusEnum.COMPLETED
            ):
                # Update table status
                await self.table_repository.update_table(
                    game.table_id,
                    {"status": GameStatusEnum.COMPLETED},
                )

                # Update user stats
                for player in game.players:
                    user_id = player.user_id
                    profit = player.net_profit

                    duration = game.duration or Duration()
                    hours_played = duration.hours + (duration.minutes / 60)
                    user_stats = UserStats(
                        total_profit=profit, tables_played=1, hours_played=hours_played
                    )
                    await self.user_repository.update_user_stats(
                        user_id, user_stats, "stats"
                    )

                    month = game.date.strftime("%b %Y")
                    user_monthly_stats = MonthlyStats(
                        month=month,
                        profit=profit,
                        win_rate=0,
                        tables_played=1,
                        hours_played=hours_played,
                    )
                    await self.user_repository.update_user_monthly_stats(user_id, month, user_monthly_stats)
                    await self.user_repository.update_win_rates(user_id)

            return updated_game
        except Exception as e:
            raise DatabaseError(f"Failed to update game: {str(e)}")

    async def get_recent_games(self, user_id: str, limit: int) -> List[GameDBResponse]:
        try:
            return await self.repository.get_recent_games(user_id, limit)
        except Exception as e:
            logger.error(f"Failed to get recent games for user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to get recent games: {str(e)}")

    async def count_games_for_table(self, table_id: str) -> int:
        """Count the number of games associated with a table."""
        try:
            return await self.repository.count_games_for_table(table_id)
        except Exception as e:
            logger.error(f"Failed to count games for table {table_id}: {str(e)}")
            raise DatabaseError(f"Failed to count games: {str(e)}")

    async def validate_game_access(self, game: GameDBResponse, user_id: str) -> None:
        """Validate if a user has access to a game."""
        if not game:
            raise ResourceNotFoundError("Game not found")

        user_is_player = any(player.user_id == str(user_id) for player in game.players)
        user_is_creator = str(game.creator_id) == str(user_id)

        if not (user_is_player or user_is_creator):
            raise InvalidInputError("Access denied")

    async def validate_game_creator(self, game: GameDBResponse, user_id: str) -> None:
        """Validate if a user is the creator of a game."""
        if not game:
            raise ResourceNotFoundError("Game not found")

        if str(game.creator_id) != str(user_id):
            raise InvalidInputError("Only the creator can modify the game")

    async def validate_game_state(
        self, game: GameDBResponse, required_status: Optional[GameStatusEnum] = None
    ) -> None:
        """Validate if a game is in the required state for an operation."""
        if not game:
            raise ResourceNotFoundError("Game not found")

        if required_status and game.status != required_status:
            raise GameStateError(
                f"Game must be in {required_status} state for this operation"
            )
