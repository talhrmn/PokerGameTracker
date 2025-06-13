import { api } from "@/app/clients/api-client";
import { FriendsProps, FriendsResponse } from "@/app/dashboard/friends/types";

class FriendsApiClient {
    async getFriends(): Promise<FriendsResponse> {
        return api.getData<FriendsResponse>("/friends")
    }

    async addFriend(friend_id: string): Promise<FriendsResponse> {
        return api.postData(`/friends/${friend_id}`, {})
    }

    async removeFriend(friend_id: string): Promise<FriendsResponse> {
        return api.deleteData(`/friends/${friend_id}`, {})
    }

    async searchFriend(friendRegex: string): Promise<FriendsProps[]> {
        return api.getData(`/friends/search/${friendRegex}`, {})
    }
}

export const friendsApiClient = new FriendsApiClient();
