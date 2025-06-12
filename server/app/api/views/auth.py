from app.api.dependencies import get_auth_service, get_user_service
from app.core.exceptions import DatabaseError, InvalidInputError
from app.core.security import verify_password
from app.schemas.auth import LoginResponse
from app.schemas.user import UserCreate
from app.services.auth import AuthService
from app.services.user import UserService
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post(
    "/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user."""
    # Check for existing username
    existing_username = await user_service.get_user_by_username(
        username=user_data.username
    )
    if existing_username:
        raise InvalidInputError("Username already registered")

    # Check for existing email
    existing_email = await user_service.get_user_by_email(email=user_data.email)
    if existing_email:
        raise InvalidInputError("Email already registered")

    try:
        new_user = await user_service.create_user(user_data=user_data)
        login_response = await auth_service.login_user(user=new_user)
        return login_response
    except Exception as e:
        raise DatabaseError(f"User registration failed: {str(e)}")


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login a user."""
    existing_user = await user_service.get_user_by_username(username=form_data.username)

    if not existing_user or not verify_password(
        form_data.password, existing_user.password_hash
    ):
        raise InvalidInputError("Incorrect username or password")

    try:
        login_response = await auth_service.login_user(user=existing_user)
        return login_response
    except Exception as e:
        raise DatabaseError(f"Login failed: {str(e)}")
