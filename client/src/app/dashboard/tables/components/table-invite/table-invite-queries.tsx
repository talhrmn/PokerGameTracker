import { api } from "@/app/clients/api-client";
import { tablesApiClient } from "@/app/clients/tables-api-client";
import { FriendsResponse } from "@/app/dashboard/friends/types";
import { SendInviteType } from "@/app/dashboard/tables/components/table-invite/types";
import { Table } from "@/app/dashboard/tables/types";
import { useMutation, useQuery } from "@tanstack/react-query";

export const useFetchFriendsQuery = () => {
	return useQuery({
		queryKey: ["friends-list"],
		queryFn: () => api.getData<FriendsResponse>("/friends"),
	});
};

export const useSendInvite = () => {
	return useMutation<Table, unknown, SendInviteType>({
		mutationFn: (params) => tablesApiClient.sendTableInvite(params),
		onSuccess: () => alert("Invites Sent Successfully!"),
		onError: () => alert("Failed to send invitation"),
	});
};
