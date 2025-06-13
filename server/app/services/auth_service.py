import logging
from datetime import timedelta

from app.core.exceptions import AuthenticationException
from app.core.security import create_access_token
from app.schemas.auth import LoginResponse
from app.schemas.py_object_id import PyObjectId


class AuthService:
    """
    Service for handling user authentication and token management.
    
    This service handles:
    - User login and token generation
    - Access token creation and management
    - Token expiration handling
    
    The service provides methods to:
    - Create access tokens with proper expiration
    - Handle user login and token response
    - Validate token data
    """

    def __init__(self, token_exp: int):
        """
        Initialize the authentication service.
        
        Args:
            token_exp: Token expiration time in minutes
        """
        self.token_exp = token_exp
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_access_token(self, user_id: PyObjectId) -> str:
        """
        Create an access token for a user.
        
        Args:
            user_id: The ID of the user to create token for
            
        Returns:
            str: The generated access token
            
        Raises:
            AuthenticationException: If token creation fails
        """
        try:
            if not user_id:
                raise AuthenticationException(detail="Invalid user ID")

            access_token_expires = timedelta(minutes=self.token_exp)
            access_token = create_access_token(
                data={"sub": str(user_id)},
                expires_delta=access_token_expires
            )
            return access_token
        except Exception as e:
            self.logger.error(f"Error creating access token: {e}")
            raise AuthenticationException(detail="Failed to create access token")

    def login_user(self, user_id: PyObjectId) -> LoginResponse:
        """
        Handle user login and return authentication response.
        
        Args:
            user_id: The ID of the user to login
            
        Returns:
            LoginResponse: Object containing access token and type
            
        Raises:
            AuthenticationException: If login process fails
        """
        try:
            if not user_id:
                raise AuthenticationException(detail="Invalid user ID")

            access_token = self._create_access_token(user_id)
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
            )
        except AuthenticationException:
            raise
        except Exception as e:
            self.logger.error(f"Error during user login: {e}")
            raise AuthenticationException(detail="Failed to process login")
