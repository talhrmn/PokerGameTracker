from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_user_service, get_auth_service
from app.core.security import verify_password
from app.schemas.auth import LoginResponse
from app.schemas.user import UserInput
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserInput,
        user_service: UserService = Depends(get_user_service),
        auth_service: AuthService = Depends(get_auth_service)):
    existing_username = await user_service.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    existing_email = await user_service.get_user_by_email(str(user_data.email))
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        user = await user_service.create_user(user_data=user_data)
        return auth_service.login_user(user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User registration failed: {e}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                user_service: UserService = Depends(get_user_service),
                auth_service: AuthService = Depends(get_auth_service)):
    user = await user_service.get_user_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.login_user(user.id)
