import logging
from typing import List, Set, Optional

from app.core.exceptions import ValidationException
from app.schemas.friends import FriendsResponse
from app.schemas.user import UserResponse, UserDBOutput


class FriendsService:
    """
    Service for managing and categorizing user friendships.
    
    This service handles:
    - Categorization of friends into mutual, outgoing, and incoming
    - Friend list filtering and processing
    - Friend relationship validation
    
    The service provides methods to:
    - Process and categorize friend lists
    - Filter friends by relationship type
    - Handle friend data validation
    """

    def __init__(self):
        """Initialize the friends service with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def categorize_friends(
            self,
            user_friends: Optional[List[UserDBOutput]],
            invited_friends: Optional[List[UserDBOutput]]
    ) -> FriendsResponse:
        """
        Categorize friends into mutual, outgoing, and incoming relationships.
        
        Args:
            user_friends: List of users who are friends with the current user
            invited_friends: List of users who have invited the current user
            
        Returns:
            FriendsResponse: Object containing categorized friend lists
            
        Raises:
            ValidationException: If friend data is invalid or processing fails
        """
        try:
            # Initialize empty lists if None
            user_friends = user_friends or []
            invited_friends = invited_friends or []

            # Create sets of friend IDs for efficient comparison
            user_friend_ids: Set[str] = {str(u.id) for u in user_friends}
            invited_friend_ids: Set[str] = {str(u.id) for u in invited_friends}

            # Categorize friend relationships
            mutual_ids = user_friend_ids.intersection(invited_friend_ids)
            outgoing_ids = user_friend_ids.difference(invited_friend_ids)
            incoming_ids = invited_friend_ids.difference(user_friend_ids)

            def filter_by_ids(lst: List[UserDBOutput], id_set: Set[str]) -> List[UserResponse]:
                """
                Filter a list of users by their IDs.
                
                Args:
                    lst: List of users to filter
                    id_set: Set of user IDs to filter by
                    
                Returns:
                    List[UserResponse]: Filtered list of users
                """
                try:
                    return [UserResponse(**u.model_dump()) for u in lst if str(u.id) in id_set]
                except Exception as e:
                    self.logger.error(f"Error filtering users by IDs: {e}")
                    raise ValidationException(detail="Failed to process friend data")

            # Filter and categorize friends
            mutual_friends = filter_by_ids(user_friends, mutual_ids)
            outgoing_friends = filter_by_ids(user_friends, outgoing_ids)
            incoming_friends = filter_by_ids(invited_friends, incoming_ids)

            return FriendsResponse(
                friends=mutual_friends,
                friends_invited=outgoing_friends,
                friend_invites=incoming_friends
            )
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error categorizing friends: {e}")
            raise ValidationException(detail="Failed to categorize friends")
