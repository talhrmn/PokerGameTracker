import logging
from datetime import UTC, datetime
from typing import List, Optional

from bson import ObjectId

from app.core.exceptions import (
    DatabaseException,
    DuplicateResourceException,
    NotFoundException,
    ValidationException, AuthenticationException
)
from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserInput, UserDBInput, UserDBOutput, UserDBAuthOutput
from app.services.base import BaseService


class UserService(BaseService[UserInput, UserDBOutput]):
    """
    Service for user-related business logic.
    
    This service handles all user-related operations, including:
    - User registration and authentication
    - User profile management
    - User statistics and analytics
    - Friend management
    - User search functionality
    
    Type Parameters:
        UserInput: Pydantic model for user input/creation
        UserDBOutput: Pydantic model for user responses
    """

    def __init__(self, repository: UserRepository):
        """
        Initialize the user service.
        
        Args:
            repository: UserRepository instance for database operations
        """
        super().__init__(repository)
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_auth_user(self, username: str) -> Optional[UserDBAuthOutput]:
        """
        Get a user auth details.

        Args:
            username: The username to search for

        Returns:
            Optional[UserDBAuthOutput]: The user if found, None otherwise
        """
        user = await self.repository.get_auth_user(username)
        if not user:
            raise AuthenticationException(detail="User does not exist, please sign up!")
        try:
            return UserDBAuthOutput(**user)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user by username: {str(e)}")

    async def get_user_by_username(self, username: str) -> Optional[UserDBOutput]:
        """
        Get a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            Optional[UserDBOutput]: The user if found, None otherwise
            
        Raises:
            DatabaseException: If there's an error fetching the user
        """
        try:
            return await self.repository.get_by_username(username)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user by username: {str(e)}")

    async def get_user_by_email(self, email: str) -> Optional[UserDBOutput]:
        """
        Get a user by their email.
        
        Args:
            email: The email to search for
            
        Returns:
            Optional[UserDBOutput]: The user if found, None otherwise
            
        Raises:
            DatabaseException: If there's an error fetching the user
        """
        try:
            return await self.repository.get_by_email(email)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user by email: {str(e)}")

    async def create_user(self, user_data: UserInput) -> Optional[UserDBOutput]:
        """
        Create a new user.
        
        Args:
            user_data: The user data to create
            
        Returns:
            Optional[UserDBOutput]: The created user if successful, None otherwise
            
        Raises:
            DuplicateResourceException: If username or email already exists
            DatabaseException: If there's an error creating the user
        """
        try:
            user = await self.repository.get_by_username(user_data.username)
            if user:
                raise DuplicateResourceException(detail="Username already exists")
            user = await self.repository.get_by_email(str(user_data.email))
            if user:
                raise DuplicateResourceException(detail="Email already exists")

            password_hash = get_password_hash(user_data.password)
            user_input = UserDBInput(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                last_login=datetime.now(UTC),
            )

            return await self.repository.create(user_input)
        except DatabaseException as e:
            raise DatabaseException(detail=f"User creation failed: {str(e)}")
        except DuplicateResourceException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error during user creation: {str(e)}")

    async def update_login(self, user_id: str) -> UserDBOutput:
        """
        Update a user's last login timestamp.
        
        Args:
            user_id: The ID of the user to update
            
        Returns:
            UserDBOutput: The updated user
            
        Raises:
            DatabaseException: If there's an error updating the login time
        """
        try:
            return await self.repository.update_login(user_id)
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to update login time: {str(e)}")
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error during login update: {str(e)}")

    async def update_user_data(self, user_id: str, update_data: dict) -> Optional[UserDBOutput]:
        """
        Update a user's profile data.
        
        Args:
            user_id: The ID of the user to update
            update_data: Dictionary of fields to update
            
        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise
            
        Raises:
            DuplicateResourceException: If username or email is already taken
            DatabaseException: If there's an error updating the user
        """
        try:
            if "username" in update_data:
                user = await self.get_user_by_username(update_data["username"])
                if user and str(user.id) != user_id:
                    raise DuplicateResourceException(detail="Username already taken")
            if "email" in update_data:
                user = await self.get_user_by_email(update_data["email"])
                if user and str(user.id) != user_id:
                    raise DuplicateResourceException(detail="Email already taken")
            return await self.repository.update(user_id, update_data)
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to update user data: {str(e)}")
        except DuplicateResourceException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error during user update: {str(e)}")

    async def get_user_friends(self, user_id: str) -> Optional[List[UserDBOutput]]:
        """
        Get a user's friends list.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Optional[List[UserDBOutput]]: List of friends if found, None otherwise
            
        Raises:
            DatabaseException: If there's an error fetching friends
        """
        try:
            return await self.repository.get_user_friends(user_id)
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to get user friends: {str(e)}")
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error getting user friends: {str(e)}")

    async def get_user_invited_friends(self, user_id: str) -> Optional[List[UserDBOutput]]:
        """
        Get users who have invited this user as a friend.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Optional[List[UserDBOutput]]: List of users who invited this user
            
        Raises:
            DatabaseException: If there's an error fetching invited friends
        """
        try:
            return await self.repository.get_user_invited_friends(user_id)
        except DatabaseException as e:
            raise DatabaseException(detail=f"Failed to get invited friends: {str(e)}")
        except Exception as e:
            raise DatabaseException(detail=f"Unexpected error getting invited friends: {str(e)}")

    async def add_friend(self, user_id: str, friend_id: str) -> None:
        """
        Add a friend relationship between two users.
        
        Args:
            user_id: The ID of the first user
            friend_id: The ID of the second user
            
        Raises:
            ValidationException: If friend ID is invalid
            NotFoundException: If friend user not found
            DatabaseException: If there's an error adding the friend
        """
        try:
            if not ObjectId.is_valid(friend_id):
                raise ValidationException(detail="Invalid friend ID")
            friend = await self.get_by_id(friend_id)
            if not friend:
                raise NotFoundException(detail="Friend user not found")
            await self.repository.add_friend(user_id, friend_id)
        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to add friend: {str(e)}")

    async def remove_friend(self, user_id: str, friend_id: str) -> None:
        """
        Remove a friend relationship between two users.
        
        Args:
            user_id: The ID of the first user
            friend_id: The ID of the second user
            
        Raises:
            ValidationException: If friend ID is invalid
            DatabaseException: If there's an error removing the friend
        """
        try:
            if not ObjectId.is_valid(friend_id):
                raise ValidationException(detail="Invalid friend ID")
            await self.repository.remove_friend(user_id, friend_id)
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(detail=f"Failed to remove friend: {str(e)}")

    async def search_users(self, user_id: str, friend_regex: str) -> List[UserDBOutput]:
        """
        Search for users by username or email.
        
        Args:
            user_id: The ID of the user performing the search
            friend_regex: The search pattern to match against usernames and emails
            
        Returns:
            List[UserDBOutput]: List of matching users
            
        Raises:
            DatabaseException: If there's an error searching users
        """
        try:
            return await self.repository.search_users(user_id, friend_regex)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to search users: {str(e)}")
