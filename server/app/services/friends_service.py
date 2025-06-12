from typing import List, Set, Optional

from app.schemas.friends import FriendsResponse
from app.schemas.user import UserResponse, UserDBOutput


class FriendsService:
    def __init__(self):
        pass

    def categorize_friends(
            self,
            user_friends: Optional[List[UserDBOutput]],
            invited_friends: Optional[List[UserDBOutput]]
    ) -> FriendsResponse:
        user_friend_ids: Set[str] = {str(u.id) for u in user_friends}
        invited_friend_ids: Set[str] = {str(u.id) for u in invited_friends}

        # Mutual friends: in both sets
        mutual_ids = user_friend_ids.intersection(invited_friend_ids)
        # Outgoing: in user_friend_ids but not in invited_friend_ids
        outgoing_ids = user_friend_ids.difference(invited_friend_ids)
        # Incoming: in invited_friend_ids but not in user_friend_ids
        incoming_ids = invited_friend_ids.difference(user_friend_ids)

        # Helper: filter list by id set
        def filter_by_ids(lst: List[UserDBOutput], id_set: Set[str]) -> List[UserResponse]:
            return [UserResponse(**u.model_dump()) for u in lst if str(u.id) in id_set]

        mutual_friends = filter_by_ids(user_friends, mutual_ids)
        outgoing_friends = filter_by_ids(user_friends, outgoing_ids)
        incoming_friends = filter_by_ids(invited_friends, incoming_ids)

        return FriendsResponse(
            friends=mutual_friends,
            friends_invited=outgoing_friends,
            friend_invites=incoming_friends
        )
