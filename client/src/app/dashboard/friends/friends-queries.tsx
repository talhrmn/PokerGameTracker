import { friendsApiClient } from "@/app/clients/friends-api-client";
import { FriendsProps } from "@/app/dashboard/friends/types";
import { useMutation, useQuery } from "@tanstack/react-query";
import { message } from "antd";

export const useFriendsQuery = () => {
	return useQuery({
		queryKey: ["friends", "friendsInvited", "friendInvites"],
		queryFn: () => friendsApiClient.getFriends(),
		retry: 1,
		select: (data) => ({
			friends: (data.friends || []) as FriendsProps[],
			friendsInvited: (data.friends_invited || []) as FriendsProps[],
			friendInvites: (data.friend_invites || []) as FriendsProps[],
		}),
	});
};

// export const useAddFriend = () => {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: (friend_id: string) =>
//       api.postData(`/friends/${friend_id}`, {}),
//     onSuccess: () =>
//       queryClient.invalidateQueries({
//         queryKey: ["friends", "friendsInvited", "friendInvites"],
//       }),
//     onError: () => message.error("Failed to add friend"),
//   });
// };

// export const useRemoveFriend = () => {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: (friend_id: string) =>
//       api.deleteData(`/friends/${friend_id}`, {}),
//     onSuccess: () => queryClient.invalidateQueries({ queryKey: ["friends"] }),
//     onError: () => message.error("Failed to remove friend"),
//   });
// };

export const useSearchFriend = () => {
	return useMutation<FriendsProps[], unknown, string>({
		mutationFn: (friendRegex) => friendsApiClient.searchFriend(friendRegex),
		onSuccess: (data) => data as FriendsProps[],
		onError: () => message.error("Failed to find friend"),
	});
};
