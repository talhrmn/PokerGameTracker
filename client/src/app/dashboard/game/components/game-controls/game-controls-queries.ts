import { gamesApiClient } from "@/app/clients/games-api-client";
import { GameProps } from "@/app/dashboard/games/types";
import { useMutation } from "@tanstack/react-query";

export const useGameCompletion = () => {
  return useMutation<GameProps, unknown, string>({
    mutationFn: (gameId) => gamesApiClient.completeGame(gameId),
    onSuccess: () => alert("Game Ended Successfully!"),
    onError: () => alert("Failed Ending Game"),
  });
};
