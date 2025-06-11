import { api } from "@/app/clients/api-client";
import { gamesApiClient } from "@/app/clients/games-api-client";
import { GameProps } from "@/app/dashboard/games/types";
import { useQuery } from "@tanstack/react-query";

export const useTotalGamesCountQuery = () => {
	return useQuery({
		queryKey: ["total-games-count"],
		queryFn: () => gamesApiClient.getTotalNumberOfGames(),
	});
};

export const useFetchGamesQuery = (limit: number, skip: number) => {
	return useQuery<GameProps[], unknown>({
		queryKey: ["games", limit, skip],
		queryFn: () => gamesApiClient.getGames(limit, skip),
		staleTime: 5 * 60 * 1000,
	});
};
