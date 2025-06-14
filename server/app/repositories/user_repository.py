import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.exceptions import DatabaseException
from app.repositories.base import BaseRepository
from app.schemas.user import UserDBInput, UserDBOutput, UserDBAuthOutput


class UserRepository(BaseRepository[UserDBInput, UserDBOutput]):
    """
    Repository for users collection.
    
    This repository handles all database operations related to users, including:
    - User CRUD operations (inherited from BaseRepository)
    - User authentication and login tracking
    - Friend management
    - User search functionality
    
    Type Parameters:
        UserDBInput: Pydantic model for user creation/updates
        UserDBOutput: Pydantic model for user responses
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        """
        Initialize the user repository.
        
        Args:
            db_client: MongoDB client instance
        """
        super().__init__(db_client.users, UserDBInput, UserDBOutput)
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_auth_user(self, username: str) -> Optional[dict]:
        """
        Get a user auth details.

        Args:
            username: The username to search for

        Returns:
            Optional[UserDBAuthOutput]: The user if found, None otherwise
        """
        return await self.get_one_by_query({"username": username}, dump_model=False)

    async def get_by_username(self, username: str) -> Optional[UserDBOutput]:
        """
        Get a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            Optional[UserDBOutput]: The user if found, None otherwise
        """
        return await self.get_one_by_query({"username": username})

    async def get_by_email(self, email: str) -> Optional[UserDBOutput]:
        """
        Get a user by their email.
        
        Args:
            email: The email to search for
            
        Returns:
            Optional[UserDBOutput]: The user if found, None otherwise
        """
        return await self.get_one_by_query({"email": email})

    async def update_login(self, user_id: str) -> Optional[UserDBOutput]:
        """
        Update a user's last login timestamp.
        
        Args:
            user_id: The ID of the user to update
            
        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error updating the login time
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise DatabaseException(detail="Invalid user ID")
            update_data = {"last_login": datetime.now(UTC)}
            return await self.update(user_id, update_data)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update login time: {str(e)}")

    async def get_user_friends(self, user_id: str) -> List[UserDBOutput]:
        """
        Get a user's friends list.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[UserDBOutput]: List of friends
            
        Raises:
            DatabaseException: If there's an error fetching friends
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            query = {"_id": ObjectId(user_id)}
            projection = {"friends": 1}
            user = await self.get_one_by_query(query, projection, dump_model=False)
            if not user or not user.get("friends"):
                return []
            friend_ids = [ObjectId(fid) for fid in user.get("friends", [])]
            list_filter = {"_id": {"$in": friend_ids}}
            list_projection = {"password_hash": 0}
            friends_list = await self.list(list_filter, list_projection)
            return friends_list
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get user friends: {str(e)}")

    async def get_user_invited_friends(self, user_id: str) -> List[UserDBOutput]:
        """
        Get users who have invited this user as a friend.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[UserDBOutput]: List of users who invited this user
            
        Raises:
            DatabaseException: If there's an error fetching invited friends
        """
        try:
            if not ObjectId.is_valid(user_id):
                return []
            list_filter = {"friends": user_id}
            list_projection = {"password_hash": 0}
            friends_list = await self.list(list_filter, list_projection)
            return friends_list
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get invited friends: {str(e)}")

    async def add_friend(self, user_id: str, friend_id: str) -> None:
        """
        Add a friend relationship between two users.
        
        Args:
            user_id: The ID of the first user
            friend_id: The ID of the second user
            
        Raises:
            DatabaseException: If there's an error adding the friend
        """
        try:
            if not (ObjectId.is_valid(user_id) and ObjectId.is_valid(friend_id)):
                raise DatabaseException(detail="Invalid user ID(s)")
            uid = ObjectId(user_id)
            fid = ObjectId(friend_id)
            result1 = await self.collection.update_one(
                {"_id": uid, "friends": {"$ne": fid}},
                {"$push": {"friends": fid}}
            )
            result2 = await self.collection.update_one(
                {"_id": fid, "friends": {"$ne": uid}},
                {"$push": {"friends": uid}}
            )
            if not (result1.acknowledged and result2.acknowledged):
                raise DatabaseException(detail="Failed to add friend relationship")
        except Exception as e:
            raise DatabaseException(detail=f"Failed to add friend: {str(e)}")

    async def remove_friend(self, user_id: str, friend_id: str) -> None:
        """
        Remove a friend relationship between two users.
        
        Args:
            user_id: The ID of the first user
            friend_id: The ID of the second user
            
        Raises:
            DatabaseException: If there's an error removing the friend
        """
        try:
            if not (ObjectId.is_valid(user_id) and ObjectId.is_valid(friend_id)):
                raise DatabaseException(detail="Invalid user ID(s)")
            uid = ObjectId(user_id)
            fid = ObjectId(friend_id)
            result1 = await self.collection.update_one({"_id": uid}, {"$pull": {"friends": fid}})
            result2 = await self.collection.update_one({"_id": fid}, {"$pull": {"friends": uid}})
            if not (result1.acknowledged and result2.acknowledged):
                raise DatabaseException(detail="Failed to remove friend relationship")
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
            if not ObjectId.is_valid(user_id):
                return []
            regex_filter = {"$regex": friend_regex, "$options": "i"}
            list_filter = {
                "_id": {"$ne": ObjectId(user_id)},
                "$or": [
                    {"username": regex_filter},
                    {"email": regex_filter}
                ]
            }
            list_projection = {"password_hash": 0}
            return await self.list(list_filter, list_projection)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to search users: {str(e)}")
