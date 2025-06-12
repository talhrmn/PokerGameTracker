from app.api.views import auth, friends, games, sse, statistics, tables, trends, users
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(friends.router, prefix="/friends", tags=["Friends"])
api_router.include_router(tables.router, prefix="/tables", tags=["Tables"])
api_router.include_router(games.router, prefix="/games", tags=["Games"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(trends.router, prefix="/trends", tags=["Trends"])
api_router.include_router(sse.router, prefix="/events", tags=["Events"])
