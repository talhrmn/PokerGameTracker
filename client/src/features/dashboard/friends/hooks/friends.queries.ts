import { friendsService } from "@/features/dashboard/friends/services/friends.service";
import { FriendsProps } from "@/features/dashboard/friends/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { message } from "antd";

export const useFriendsQuery = () => {
	return useQuery({
		queryKey: ["friends", "friendsInvited", "friendInvites"],
		queryFn: () => friendsService.getFriends(),
		retry: 1,
		select: (data) => ({
			friends: (data.friends || []) as FriendsProps[],
			friendsInvited: (data.friends_invited || []) as FriendsProps[],
			friendInvites: (data.friend_invites || []) as FriendsProps[],
		}),
	});
};

export const useAddFriend = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (friend_id: string) => friendsService.addFriend(friend_id),
		onSuccess: () =>
			queryClient.invalidateQueries({
				queryKey: ["friends", "friendsInvited", "friendInvites"],
			}),
		onError: () => message.error("Failed to add friend"),
	});
};

export const useRemoveFriend = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (friend_id: string) => friendsService.removeFriend(friend_id),
		onSuccess: () => queryClient.invalidateQueries({ queryKey: ["friends"] }),
		onError: () => message.error("Failed to remove friend"),
	});
};

export const useSearchFriend = (searchTerm: string) => {
	return useQuery({
	  queryKey: ['friends', 'search', searchTerm],
	  queryFn: () => friendsService.searchFriend(searchTerm),
	  enabled: searchTerm.length > 0,
	  staleTime: 5 * 60 * 1000,
	});
  };
