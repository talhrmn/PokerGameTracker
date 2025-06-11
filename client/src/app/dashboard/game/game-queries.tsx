import { gamesApiClient } from "@/app/clients/games-api-client";
import { BASE_URL } from "@/app/consts";
import { GameProps } from "@/app/dashboard/games/types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

export const useGameQuery = (game_id: string) => {
	return useQuery({
		queryKey: ["game"],
		queryFn: () => gamesApiClient.getGame(game_id),
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
				// console.log("Game update received:", updatedGame);
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
