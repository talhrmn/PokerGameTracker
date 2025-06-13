from contextlib import asynccontextmanager

import uvicorn
from bson.errors import InvalidId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.api import api_router
from app.core.config import settings
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    invalid_id_exception_handler,
    general_exception_handler
)
from app.core.exceptions import AppException
from app.db.mongo_client import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(InvalidId, invalid_id_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Poker Tracker API", "docs": f"{settings.API_PREFIX}/docs"}


if __name__ == "__main__":
    uvicorn.run("server.app.main:app", host="0.0.0.0", port=8000, reload=True)
