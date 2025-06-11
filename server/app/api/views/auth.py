from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.dependencies import get_database
from app.core.security import verify_password
from app.handlers.auth import auth_handler
from app.handlers.users import user_handler
from app.schemas.auth import LoginResponse
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db_client: AsyncIOMotorClient = Depends(get_database)):
    existing_username = await user_handler.get_user_by_username(username=user_data.username, db_client=db_client)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    existing_email = await user_handler.get_user_by_email(email=user_data.email, db_client=db_client)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        new_user = await user_handler.create_user(user_data=user_data, db_client=db_client)
        login_response = await auth_handler.login_user(user=new_user, db_client=db_client)
        return login_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User registration failed: {e}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db_client: AsyncIOMotorClient = Depends(get_database)):
    existing_user = await user_handler.get_user_by_username(username=form_data.username, db_client=db_client)

    if not existing_user or not verify_password(form_data.password, existing_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_response = await auth_handler.login_user(user=existing_user, db_client=db_client)
    return login_response
