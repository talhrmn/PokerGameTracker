import { api } from "@/clients/api-client";
import { GameProps } from "@/features/dashboard/game/types/games.types";
import { PlayerChangeProps } from "@/features/dashboard/game/types/player-details.types";

class GameService {
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

    async addPlayerBuyIn(gameId: string, buyIn: PlayerChangeProps): Promise<GameProps> {
        return api.putData<PlayerChangeProps, GameProps>(`/games/${gameId}/buyin`, buyIn);
    }

    async playerCashOut(gameId: string, cashOut: PlayerChangeProps): Promise<GameProps> {
        return api.putData<PlayerChangeProps, GameProps>(`/games/${gameId}/cashout`, cashOut);
    }
}

export const gameService = new GameService();
