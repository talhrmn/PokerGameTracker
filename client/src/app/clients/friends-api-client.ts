import { api } from "@/app/clients/api-client";
import { FriendsProps, FriendsResponse } from "@/app/dashboard/friends/types";

class FriendsApiClient {
    async getFriends(): Promise<FriendsResponse> {
        return api.getData<FriendsResponse>("/friends")
    }

    async searchFriend(friendRegex: string): Promise<FriendsProps[]> {
        return api.getData(`/friends/search/${friendRegex}`, {})
    }
}

export const friendsApiClient = new FriendsApiClient();
