from typing import List

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from server.app.api.dependencies import get_database, get_current_user
from server.app.handlers.statistics import statistics_handler
from server.app.schemas.user import UserResponse, MonthlyStats

router = APIRouter()


@router.get("/monthly", response_model=List[MonthlyStats])
async def get_monthly_stats(current_user: UserResponse = Depends(get_current_user),
                            db_client: AsyncIOMotorClient = Depends(get_database)) -> List[MonthlyStats]:
    user_monthly_stats = await statistics_handler.get_monthly_statistics(user=current_user, db_client=db_client)
    return user_monthly_stats
