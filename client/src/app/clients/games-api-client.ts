import { api } from "@/app/clients/api-client";
import { GameProps } from "@/app/dashboard/games/types";

class GamesApiClient {
    async getGame(gameId: string): Promise<GameProps> {
        return api.getData<GameProps>(`/games/${gameId}`)
    }

    async getGames(limit: number, skip: number): Promise<GameProps[]> {
        return api.getData<GameProps[]>("/games/", {
            limit: limit,
            skip: skip,
          })
    }

    async getTotalNumberOfGames(): Promise<number> {
        return api.getData<number>("/games/count")
    }

    async startGame(params: Record<string, unknown>): Promise<GameProps> {
        return api.postData("/games", params);
    }

    async completeGame(gameId: string): Promise<GameProps> {
        return api.postData<unknown, GameProps>(`/games/${gameId}/end`, {});
    }
}

export const gamesApiClient = new GamesApiClient();
