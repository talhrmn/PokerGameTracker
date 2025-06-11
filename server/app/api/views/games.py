from datetime import UTC, datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient

from server.app.api.dependencies import get_current_user, get_database
from server.app.handlers.games import game_handler
from server.app.handlers.sse import sse_handler
from server.app.handlers.tables import table_handler
from server.app.schemas.game import GameUpdate, GameDBInput, GameBase, GameStatusEnum, GameDBResponse, BuyIn, \
    CashOut, Duration
from server.app.schemas.user import UserResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GameDBResponse)
async def create_game(game: GameBase,
                      current_user: UserResponse = Depends(get_current_user),
                      db_client: AsyncIOMotorClient = Depends(get_database)) -> GameDBResponse:
    table = await table_handler.get_table_by_id(table_id=game.table_id, db_client=db_client)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    if str(table.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only table creator can start a game")

    try:
        created_game = await game_handler.create_game(game=game, user=current_user, db_client=db_client)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Game creation failed: {e}"
        )

    await table_handler.update_table(table_id=game.table_id, update_data={"game_id": str(created_game.id),
                                                                          "status": GameStatusEnum.IN_PROGRESS},
                                     db_client=db_client)
    return created_game


@router.get("/", response_model=List[GameDBResponse])
async def get_games(
        table_id: str = None,
        status: str = None,
        limit: int = None,
        skip: int = None,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    games = await game_handler.get_games_for_player(player=current_user, table_id=table_id, status=status, skip=skip,
                                                    limit=limit, db_client=db_client)
    return games


@router.get("/count", response_model=int)
async def get_games_count(
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    games_count = await game_handler.get_games_count_for_player(player=current_user, db_client=db_client)
    return games_count


@router.get("/{game_id}", response_model=GameDBInput)
async def get_game(game_id: str, current_user: UserResponse = Depends(get_current_user),
                   db_client: AsyncIOMotorClient = Depends(get_database)) -> GameDBResponse:
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game ID")

    game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    user_is_player = any(
        str(player.user_id) == str(current_user.id)
        for player in game.players
    )

    user_is_game_creator = str(game.creator_id) == str(current_user.id)

    if not (user_is_player or user_is_game_creator):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return game


@router.put("/{game_id}", response_model=Optional[GameDBResponse])
async def update_game(
        game_id: str,
        game_update: GameUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game ID")

    existing_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    if not existing_game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    table = await table_handler.get_table_by_id(table_id=existing_game.table_id, db_client=db_client)
    if not table or str(table.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the table creator can modify the game")

    update_data = {k: v for k, v in game_update.model_dump(exclude_unset=True).items() if v is not None}
    await game_handler.update_game(game_id=game_id, update_data=update_data, db_client=db_client)
    updated_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    await sse_handler.send_game_update(game_id=game_id, data=updated_game)
    return updated_game


@router.put("/{game_id}/buyin", response_model=Optional[GameDBResponse])
async def update_player_buyin(
        game_id: str,
        buyin: BuyIn,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
) -> GameDBResponse:
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game ID")

    existing_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    if not existing_game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    current_pot = existing_game.total_pot
    current_available_cash_out = existing_game.available_cash_out
    await game_handler.update_player_buyin(game_id=game_id, player_id=current_user.id, buyin=buyin,
                                           total_pot=current_pot, available_cash_out=current_available_cash_out,
                                           db_client=db_client)

    updated_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    await sse_handler.send_game_update(game_id=game_id, data=updated_game)
    return updated_game


@router.put("/{game_id}/cashout", response_model=Optional[GameDBResponse])
async def update_player_cashout(
        game_id: str,
        cash_out: CashOut,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
) -> GameDBResponse:
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game ID")

    existing_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    if not existing_game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    current_available_cash_out = existing_game.available_cash_out
    if cash_out.amount > current_available_cash_out:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cash out")

    current_player = [player for player in existing_game.players if player.user_id == current_user.id]
    if not current_player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    total_buy_ins = sum(buy_in.amount for buy_in in current_player[0].buy_ins)
    await game_handler.update_player_casheout(game_id=game_id, player_id=current_user.id,
                                              cashout=(cash_out.amount + current_player[0].cash_out),
                                              net_profit=(cash_out.amount - total_buy_ins),
                                              available_cash_out=current_available_cash_out, db_client=db_client)

    updated_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    await sse_handler.send_game_update(game_id=game_id, data=updated_game)
    return updated_game


@router.post("/{game_id}/end", response_model=Optional[GameDBResponse])
async def update_end_game(
        game_id: str,
        current_user: UserResponse = Depends(get_current_user),
        db_client: AsyncIOMotorClient = Depends(get_database)
):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game ID")

    existing_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    if not existing_game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    if str(existing_game.creator_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only game creator can end the game")

    if existing_game.available_cash_out != 0 or sum(
            player.cash_out for player in existing_game.players) != existing_game.total_pot:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cashout doesnt match buyins")

    time_diff = datetime.now(UTC) - existing_game.created_at

    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    update_data = {"status": GameStatusEnum.COMPLETED.value, "duration": Duration(
        hours=int(hours),
        minutes=int(minutes)
    ).model_dump()}
    await game_handler.update_game(game_id=game_id, update_data=update_data, existing_game=existing_game,
                                   db_client=db_client)
    updated_game = await game_handler.get_game_by_id(game_id=game_id, db_client=db_client)
    await sse_handler.send_game_update(game_id=game_id, data=updated_game)
    return updated_game
