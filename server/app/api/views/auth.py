import logging
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_user_service, get_auth_service
from app.core.exceptions import AuthenticationException
from app.core.security import verify_password
from app.schemas.auth import LoginResponse
from app.schemas.user import UserInput
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserInput,
        user_service: UserService = Depends(get_user_service),
        auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """
    Register a new user and return authentication token.
    
    Args:
        user_data: User registration data
        user_service: Service for user operations
        auth_service: Service for authentication operations
        
    Returns:
        LoginResponse: Authentication token and type
    """
    # Check for existing username
    user = await user_service.get_user_by_username(user_data.username)
    if user:
        raise AuthenticationException(detail="Username already registered")

    # Check for existing email
    user = await user_service.get_user_by_email(str(user_data.email))
    if user:
        raise AuthenticationException(detail="Email already registered")

    # Create user and return auth token
    user = await user_service.create_user(user_data=user_data)
    return auth_service.login_user(user.id)


@router.post("/login", response_model=LoginResponse)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service),
        auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """
    Authenticate user and return authentication token.
    
    Args:
        form_data: Login form data containing username and password
        user_service: Service for user operations
        auth_service: Service for authentication operations
        
    Returns:
        LoginResponse: Authentication token and type
    """
    # Get user by username
    user = await user_service.get_user_by_username(form_data.username)

    # Verify credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        raise AuthenticationException(
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Return auth token
    return auth_service.login_user(user.id)
