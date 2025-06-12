from app.api.dependencies import get_current_user, get_trends_service
from app.schemas.trends import TrendsResponse
from app.schemas.user import UserResponse
from app.services.trends import TrendsService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/", response_model=TrendsResponse)
async def get_trends(
    current_user: UserResponse = Depends(get_current_user),
    trends_service: TrendsService = Depends(get_trends_service),
) -> TrendsResponse:
    """Get trends data for the current user."""
    return await trends_service.get_trends(current_user)
