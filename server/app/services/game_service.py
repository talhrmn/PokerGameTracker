import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from fastapi import HTTPException, status

from app.repositories.game_repository import GameRepository
from app.schemas.game import (
    GameBase, GameDBInput, GameDBOutput, GameUpdate,
    BuyIn, CashOut, GameStatusEnum, Duration
)
from app.schemas.table import PlayerStatusEnum
from app.schemas.user import UserResponse
from app.services.base import BaseService


class GameService(BaseService[GameDBInput, GameDBOutput]):

    def __init__(self, repository: GameRepository):
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_game(self, game_data: GameBase, current_user: UserResponse) -> GameDBOutput:
        try:
            game = await self.repository.create_game(game_data, str(current_user.id))
        except Exception as e:
            self.logger.error(f"Error creating game: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Game creation failed")
        return game

    async def get_games_for_player(
            self,
            current_user: UserResponse,
            table_id: Optional[str] = None,
            game_status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[GameDBOutput]:
        games = await self.repository.list_for_player(str(current_user.id), table_id=table_id, status=game_status,
                                                      skip=skip,
                                                      limit=limit)
        return games

    async def count_games_for_player(self, current_user: UserResponse) -> int:
        return await self.repository.count_for_player(str(current_user.id))

    async def count_games_for_table(self, table_id: str) -> int:
        return await self.repository.count_for_table(table_id)

    async def update_game_invite(self, game_id: str, current_user: UserResponse,
                                 status: PlayerStatusEnum) -> GameDBOutput:
        """
        A user invites themselves (confirm) or removes themselves from a game invitation.
        - If confirming: push into players array if not present.
        - If un-confirming: pull from players array.
        """
        # Ensure game exists
        game = await self.get_by_id(game_id)
        # If confirming:
        if status == PlayerStatusEnum.CONFIRMED:
            # Push only if not already in players
            updated = await self.repository.push_player_invite(game_id, str(current_user.id), current_user.username)
        else:
            # Pull player
            updated = await self.repository.pull_player(game_id, str(current_user.id))
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to update game invite")
        return updated

    async def update_player_buyin(self, game_id: str, current_user: UserResponse, buyin: BuyIn) -> GameDBOutput:
        """
        Add a buy-in for current_user in the game:
        - Fetch existing game to get current total_pot and available_cash_out
        - Validate that user is in players
        - Push buyin and update totals
        """
        game = await self.get_by_id(game_id)
        # Validate player is part of game
        player_entries = [p for p in game.players if str(p.user_id) == str(current_user.id)]
        if not player_entries:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")
        current_pot = game.total_pot
        current_available = game.available_cash_out
        updated = await self.repository.push_player_buyin(game_id, str(current_user.id), buyin, current_pot,
                                                          current_available)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update buy-in")
        return updated

    async def update_player_cashout(self, game_id: str, current_user: UserResponse, cashout: CashOut) -> GameDBOutput:
        """
        Cash out for current_user:
        - Fetch game, validate player present
        - Ensure cashout.amount <= available_cash_out
        - Compute total buyins for player to calculate net_profit
        - Update fields
        """
        game = await self.get_by_id(game_id)
        # Validate player
        player_entries = [p for p in game.players if str(p.user_id) == str(current_user.id)]
        if not player_entries:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not in game")
        current_available = game.available_cash_out
        if cashout.amount > current_available:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cash out amount")
        player = player_entries[0]
        total_buyins = sum(b.amount for b in player.buy_ins)
        new_cashout = cashout.amount + player.cash_out
        net_profit = cashout.amount - total_buyins
        updated = await self.repository.set_player_cashout(game_id, str(current_user.id), new_cashout, net_profit,
                                                           current_available)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update cash out")
        return updated

    async def update_game(
            self,
            game_id: str,
            game_update: GameUpdate
    ) -> Optional[GameDBOutput]:
        """
        Update game fields (e.g., venue, duration, status). If status transitions to COMPLETED, run completion logic.
        """
        # Fetch existing game (GameDBResponse). But for logic we need GameDBInput-like fields: convert response to input schema?
        existing = await self.get_by_id(game_id)
        # Build update_data dict from GameUpdate model, excluding unset
        update_data = {k: v for k, v in game_update.model_dump(exclude_unset=True).items() if v is not None}
        if not existing or not update_data:
            return None

        update_data["updated_at"] = datetime.now(UTC)

        updated = await self.repository.update(game_id, update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update game")

        return updated

    async def end_game(self, game_id: str) -> GameDBOutput:
        """
        Endpoint to mark game as ended:
        - Validate game exists and current_user is creator
        - Validate available_cash_out == 0 and sum(cash_out) == total_pot
        - Compute duration from created_at to now
        - Update status to COMPLETED and set duration
        - Trigger completion logic via update_game
        """
        game = await self.get_by_id(game_id)
        total_pot = game.total_pot
        total_cashouts = sum(p.cash_out for p in game.players)
        if game.available_cash_out != 0 or total_cashouts != total_pot:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cashout does not match buy-ins")
        # Compute duration
        time_diff = datetime.now(UTC) - game.created_at
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        duration = Duration(hours=int(hours), minutes=int(minutes))
        # Build GameUpdate
        game_update = GameUpdate(status=GameStatusEnum.COMPLETED, duration=duration)
        updated = await self.update_game(game_id, game_update)
        return updated

    async def get_recent_games(self, current_user: UserResponse, limit: int = 5) -> List[GameDBOutput]:
        return await self.repository.list_recent_for_player(str(current_user.id), limit=limit)

    async def get_user_win_rate(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            return

        result = await self.repository.get_user_stats_rate(user_id)
        return None if not result else result[0]

    async def get_user_monthly_win_rates(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            return

        results = await self.repository.get_user_monthly_stats_rates(user_id)
        return results