import logging
from datetime import datetime, UTC
from typing import Optional, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.repositories.base import BaseRepository
from app.schemas.user import UserDBInput, UserDBOutput, UserStats, MonthlyStats
from app.core.exceptions import DatabaseException


class UserRepository(BaseRepository[UserDBInput, UserDBOutput]):
    """
    Repository for users collection.
    
    This repository handles all database operations related to users, including:
    - User CRUD operations (inherited from BaseRepository)
    - User authentication and login tracking
    - User statistics and monthly stats
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

    async def increment_user_stats(self, user_id: str, user_inc: UserStats) -> Optional[UserDBOutput]:
        """
        Increment a user's statistics.
        
        Args:
            user_id: The ID of the user to update
            user_inc: The statistics to increment
            
        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            inc_dict = {f"stats.{key}": value for key, value in user_inc.model_dump().items()}
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": inc_dict}
            )
            if not result.acknowledged:
                raise DatabaseException(detail="Failed to update user stats")
            return await self.get_by_id(user_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update user stats: {str(e)}")

    async def get_user_monthly_stats(self, user_id: str) -> Optional[UserDBOutput]:
        """
        Get a user's monthly statistics.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Optional[UserDBOutput]: The user's monthly stats if found, None otherwise
            
        Raises:
            DatabaseException: If there's an error fetching the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            query = {"_id": ObjectId(user_id)}
            projection = {"monthly_stats": 1}
            user = await self.get_one_by_query(query, projection, dump_model=False)
            return user.get("monthly_stats")
        except Exception as e:
            raise DatabaseException(detail=f"Failed to get monthly stats: {str(e)}")

    async def upsert_monthly_stats(self, user_id: str, month: str, user_inc: MonthlyStats) -> Optional[UserDBOutput]:
        """
        Update or insert monthly statistics for a user.
        
        Args:
            user_id: The ID of the user
            month: The month to update stats for
            user_inc: The statistics to update
            
        Returns:
            Optional[UserDBOutput]: The updated user if successful, None otherwise
            
        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
            user_query = {"_id": ObjectId(user_id), "monthly_stats.month": month}
            projection = {"monthly_stats.$": 1}
            found = await self.collection.get_one_by_query(user_query, projection, dump_model=False)
            if found and found.get("monthly_stats"):
                update_fields = ["profit", "tables_played", "hours_played"]
                inc_dict = {
                    f"monthly_stats.$.{key}": getattr(user_inc, key)
                    for key in update_fields
                    if getattr(user_inc, key, None) is not None
                }
                if not inc_dict:
                    return None
                result = await self.collection.update_one(user_query, {"$inc": inc_dict})
            else:
                data = user_inc.model_dump()
                result = await self.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$push": {"monthly_stats": data}}
                )
            if not result.acknowledged:
                raise DatabaseException(detail="Failed to update monthly stats")
            return await self.get_by_id(user_id)
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update monthly stats: {str(e)}")

    async def update_monthly_stats(self, user_id: str, month_str: str, month_win_rate: float) -> None:
        """
        Update a user's monthly win rate.
        
        Args:
            user_id: The ID of the user
            month_str: The month to update
            month_win_rate: The new win rate
            
        Raises:
            DatabaseException: If there's an error updating the stats
        """
        try:
            if not ObjectId.is_valid(user_id):
                raise DatabaseException(detail="Invalid user ID")
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id), "monthly_stats.month": month_str},
                {"$set": {"monthly_stats.$.win_rate": month_win_rate}}
            )
            if not result.acknowledged:
                raise DatabaseException(detail="Failed to update monthly win rate")
        except Exception as e:
            raise DatabaseException(detail=f"Failed to update monthly win rate: {str(e)}")

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
