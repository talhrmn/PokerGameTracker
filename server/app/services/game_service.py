import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from fastapi import HTTPException, status

from app.core.exceptions import (
    DatabaseException,
    NotFoundException,
    ValidationException,
    BusinessRuleException
)
from app.repositories.game_repository import GameRepository
from app.schemas.game import (
    GameBase, GameDBInput, GameDBOutput, GameUpdate,
    BuyIn, CashOut, GameStatusEnum, Duration
)
from app.schemas.table import PlayerStatusEnum
from app.schemas.user import UserResponse
from app.services.base import BaseService


class GameService(BaseService[GameDBInput, GameDBOutput]):
    """
    Service for game-related business logic.
    
    This service handles all game-related operations, including:
    - Game creation and management
    - Player buy-ins and cash-outs
    - Game status updates and completion
    - Game statistics and analytics
    
    Type Parameters:
        GameDBInput: Pydantic model for game input/creation
        GameDBOutput: Pydantic model for game responses
    """

    def __init__(self, repository: GameRepository):
        """
        Initialize the game service.
        
        Args:
            repository: GameRepository instance for database operations
        """
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_game(self, game_data: GameBase, current_user: UserResponse) -> GameDBOutput:
        """
        Create a new game.
        
        Args:
            game_data: The game data to create
            current_user: The user creating the game
            
        Returns:
            GameDBOutput: The created game
            
        Raises:
            DatabaseException: If there's an error creating the game
        """
        try:
            return await self.repository.create_game(game_data, str(current_user.id))
        except Exception as e:
            self.logger.error(f"Error creating game: {e}")
            raise DatabaseException(detail="Game creation failed")

    async def get_games_for_player(
            self,
            current_user: UserResponse,
            table_id: Optional[str] = None,
            game_status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[GameDBOutput]:
        """
        Get games for a specific player with optional filtering.
        
        Args:
            current_user: The user to get games for
            table_id: Optional table ID to filter by
            game_status: Optional game status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[GameDBOutput]: List of games matching the criteria
            
        Raises:
            DatabaseException: If there's an error fetching games
        """
        try:
            return await self.repository.list_for_player(
                str(current_user.id),
                table_id=table_id,
                status=game_status,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get games for player: {str(e)}")

    async def count_games_for_player(self, current_user: UserResponse) -> int:
        """
        Count total games for a player.
        
        Args:
            current_user: The user to count games for
            
        Returns:
            int: Total number of games
            
        Raises:
            DatabaseException: If there's an error counting games
        """
        try:
            return await self.repository.count_for_player(str(current_user.id))
        except Exception as e:
            raise DatabaseException(detail=f"Failed to count games for player: {str(e)}")

    async def count_games_for_table(self, table_id: str) -> int:
        """
        Count total games for a table.
        
        Args:
            table_id: The table ID to count games for
            
        Returns:
            int: Total number of games
            
        Raises:
            DatabaseException: If there's an error counting games
        """
        try:
            return await self.repository.count_for_table(table_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to count games for table: {str(e)}")

    async def update_game_invite(self, game_id: str, current_user: UserResponse,
                                 status: PlayerStatusEnum) -> GameDBOutput:
        """
        Update a player's game invitation status.
        
        Args:
            game_id: The ID of the game
            current_user: The user updating their status
            status: The new player status
            
        Returns:
            GameDBOutput: The updated game
            
        Raises:
            NotFoundException: If game not found
            DatabaseException: If there's an error updating the invite
        """
        try:
            game = await self.get_by_id(game_id)
            if not game:
                raise NotFoundException(detail="Game not found")

            if status == PlayerStatusEnum.CONFIRMED:
                updated = await self.repository.push_player_invite(game_id, str(current_user.id), current_user.username)
            else:
                updated = await self.repository.pull_player(game_id, str(current_user.id))

            if not updated:
                raise DatabaseException(detail="Failed to update game invite")
            return updated
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update game invite: {str(e)}")

    async def update_player_buyin(self, game_id: str, current_user: UserResponse, buyin: BuyIn) -> GameDBOutput:
        """
        Add a buy-in for a player in the game.
        
        Args:
            game_id: The ID of the game
            current_user: The player making the buy-in
            buyin: The buy-in details
            
        Returns:
            GameDBOutput: The updated game
            
        Raises:
            NotFoundException: If game not found or player not in game
            DatabaseException: If there's an error updating the buy-in
        """
        try:
            game = await self.get_by_id(game_id)
            if not game:
                raise NotFoundException(detail="Game not found")

            player_entries = [p for p in game.players if str(p.user_id) == str(current_user.id)]
            if not player_entries:
                raise NotFoundException(detail="Player not in game")

            current_pot = game.total_pot
            current_available = game.available_cash_out
            updated = await self.repository.push_player_buyin(
                game_id,
                str(current_user.id),
                buyin,
                current_pot,
                current_available
            )

            if not updated:
                raise DatabaseException(detail="Failed to update buy-in")
            return updated
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update buy-in: {str(e)}")

    async def update_player_cashout(self, game_id: str, current_user: UserResponse, cashout: CashOut) -> GameDBOutput:
        """
        Process a player's cash-out from the game.
        
        Args:
            game_id: The ID of the game
            current_user: The player cashing out
            cashout: The cash-out details
            
        Returns:
            GameDBOutput: The updated game
            
        Raises:
            NotFoundException: If game not found or player not in game
            ValidationException: If cash-out amount is invalid
            DatabaseException: If there's an error updating the cash-out
        """
        try:
            game = await self.get_by_id(game_id)
            if not game:
                raise NotFoundException(detail="Game not found")

            player_entries = [p for p in game.players if str(p.user_id) == str(current_user.id)]
            if not player_entries:
                raise NotFoundException(detail="Player not in game")

            current_available = game.available_cash_out
            if cashout.amount > current_available:
                raise ValidationException(detail="Invalid cash out amount")

            player = player_entries[0]
            total_buyins = sum(b.amount for b in player.buy_ins)
            new_cashout = cashout.amount + player.cash_out
            net_profit = cashout.amount - total_buyins

            updated = await self.repository.set_player_cashout(
                game_id,
                str(current_user.id),
                new_cashout,
                net_profit,
                current_available
            )

            if not updated:
                raise DatabaseException(detail="Failed to update cash out")
            return updated
        except (NotFoundException, ValidationException):
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update cash out: {str(e)}")

    async def update_game(
            self,
            game_id: str,
            game_update: GameUpdate
    ) -> Optional[GameDBOutput]:
        """
        Update game fields and handle completion logic.
        
        Args:
            game_id: The ID of the game
            game_update: The game update details
            
        Returns:
            Optional[GameDBOutput]: The updated game if successful, None otherwise
            
        Raises:
            NotFoundException: If game not found
            DatabaseException: If there's an error updating the game
        """
        try:
            game = await self.get_by_id(game_id)
            if not game:
                raise NotFoundException(detail="Game not found")

            update_data = {k: v for k, v in game_update.model_dump(exclude_unset=True).items() if v is not None}
            if not update_data:
                return None

            update_data["updated_at"] = datetime.now(UTC)
            updated = await self.update(game_id, update_data)

            if not updated:
                raise DatabaseException(detail="Failed to update game")
            return updated
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update game: {str(e)}")

    async def end_game(self, game_id: str) -> GameDBOutput:
        """
        Mark a game as completed and process final calculations.
        
        Args:
            game_id: The ID of the game to end
            
        Returns:
            GameDBOutput: The completed game
            
        Raises:
            NotFoundException: If game not found
            BusinessRuleException: If cash-out validation fails
            DatabaseException: If there's an error ending the game
        """
        try:
            game = await self.get_by_id(game_id)
            if not game:
                raise NotFoundException(detail="Game not found")

            total_pot = game.total_pot
            total_cashouts = sum(p.cash_out for p in game.players)
            if game.available_cash_out != 0 or total_cashouts != total_pot:
                raise BusinessRuleException(detail="Cashout does not match buy-ins")

            time_diff = datetime.now(UTC) - game.created_at
            hours, remainder = divmod(time_diff.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            duration = Duration(hours=int(hours), minutes=int(minutes))

            game_update = GameUpdate(status=GameStatusEnum.COMPLETED, duration=duration)
            updated = await self.update_game(game_id, game_update)
            if not updated:
                raise DatabaseException(detail="Failed to end game")
            return updated
        except (NotFoundException, BusinessRuleException):
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to end game: {str(e)}")

    async def get_recent_games(self, current_user: UserResponse, limit: int = 5) -> List[GameDBOutput]:
        """
        Get recent games for a player.
        
        Args:
            current_user: The user to get games for
            limit: Maximum number of games to return
            
        Returns:
            List[GameDBOutput]: List of recent games
            
        Raises:
            DatabaseException: If there's an error fetching games
        """
        try:
            return await self.repository.list_recent_for_player(str(current_user.id), limit=limit)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get recent games: {str(e)}")

    async def get_user_win_rate(self, user_id: str) -> Optional[dict]:
        """
        Get a user's overall win rate.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Optional[dict]: Win rate statistics if found, None otherwise
            
        Raises:
            ValidationException: If user ID is invalid
            DatabaseException: If there's an error fetching win rate
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise ValidationException(detail="Invalid user ID")

            result = await self.repository.get_user_stats_rate(user_id)
            return None if not result else result[0]
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user win rate: {str(e)}")

    async def get_user_monthly_win_rates(self, user_id: str) -> List[dict]:
        """
        Get a user's monthly win rates.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[dict]: List of monthly win rate statistics
            
        Raises:
            ValidationException: If user ID is invalid
            DatabaseException: If there's an error fetching win rates
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise ValidationException(detail="Invalid user ID")

            return await self.repository.get_user_monthly_stats_rates(user_id)
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user monthly win rates: {str(e)}")
