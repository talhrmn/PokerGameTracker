from typing import List

from app.api.dependencies import get_current_user, get_statistics_service
from app.schemas.statistics import DashboardStats
from app.schemas.user import MonthlyStats, UserResponse
from app.services.statistics import StatisticsService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/monthly", response_model=List[MonthlyStats])
async def get_monthly_stats(
    current_user: UserResponse = Depends(get_current_user),
    statistics_service: StatisticsService = Depends(get_statistics_service),
) -> List[MonthlyStats]:
    """Get monthly statistics for the current user."""
    return await statistics_service.get_monthly_stats(current_user)


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: UserResponse = Depends(get_current_user),
    statistics_service: StatisticsService = Depends(get_statistics_service),
) -> DashboardStats:
    """Get dashboard statistics for the current user."""
    return await statistics_service.get_dashboard_stats(current_user)
