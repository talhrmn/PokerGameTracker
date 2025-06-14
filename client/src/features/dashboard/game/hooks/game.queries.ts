import { BASE_URL } from "@/app/consts";
import { gameService } from "@/features/dashboard/game/services/game.service";
import { GameProps } from "@/features/dashboard/game/types/games.types";
import {
	BuyInProps,
	CashOutProps
} from "@/features/dashboard/game/types/player-details.types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

export const useGameQuery = (game_id: string) => {
	return useQuery({
		queryKey: ["game"],
		queryFn: () => gameService.getGame(game_id),
	});
};

export const useTotalGamesCountQuery = () => {
	return useQuery({
		queryKey: ["total-games-count"],
		queryFn: () => gameService.getTotalNumberOfGames(),
	});
};

export const useFetchGamesQuery = (limit: number, skip: number) => {
	return useQuery<GameProps[], unknown>({
		queryKey: ["games", limit, skip],
		queryFn: () => gameService.getGames(limit, skip),
		staleTime: 5 * 60 * 1000,
	});
};


export const useGameCompletion = () => {
	return useMutation<GameProps, unknown, string>({
	  mutationFn: (gameId) => gameService.completeGame(gameId),
	  onSuccess: () => alert("Game Ended Successfully!"),
	  onError: () => alert("Failed Ending Game"),
	});
  };

  export const useAddPlayerBuyIn = () => {
	return useMutation<GameProps, unknown, BuyInProps>({
		mutationFn: (params: BuyInProps) => gameService.addPlayerBuyIn(params.gameId, params.buyIn),
		onSuccess: () => alert("Buy In Updated Successfully!"),
		onError: () => {
			alert("Failed To Updated Buy In");
			throw new Error();
		},
	});
};

export const usePlayerCashOut = () => {
	return useMutation<GameProps, unknown, CashOutProps>({
		mutationFn: (params: CashOutProps) => gameService.playerCashOut(params.gameId, params.cashOut),
		onSuccess: () => alert("Cash Out Updated Successfully!"),
		onError: () => {
			alert("Failed To Updated Cash Out");
			throw new Error();
		},
	});
};
  

export const useGameEvents = (
	gameId: string,
	onGameUpdate: (game: GameProps) => void
) => {
	const queryClient = useQueryClient();

	useEffect(() => {
		const eventSource = new EventSource(`${BASE_URL}/events/games/${gameId}`);

		eventSource.onmessage = (event) => {
			try {
				const updatedGame = JSON.parse(event.data);
				queryClient.setQueryData(["game"], updatedGame);
				onGameUpdate(updatedGame);
			} catch (err) {
				console.error("Error parsing SSE data:", err);
			}

			eventSource.onerror = (error) => {
				console.error("SSE connection error:", error);
				eventSource.close();
			};

			return () => {
				console.log("Closing SSE connection");
				eventSource.close();
			};
		};
	}, [gameId, queryClient, onGameUpdate]);
};

// export const useUpdateGame = () => {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: ({ gameId, data }: { gameId: string; data: unknown }) =>
//       api.putData(`/games/${gameId}`, data),
//     onSuccess: (data) => queryClient.invalidateQueries({ queryKey: ["game"] }),
//   });
// };

// export const useAddPlayer = () => {
//     const queryClient = useQueryClient();

//     return useMutation({
//         mutationFn: ({gameId, playerId}: {gameId: string, playerId: string}) => api.postData(`/games/${gameId}`)
//     })
// }
