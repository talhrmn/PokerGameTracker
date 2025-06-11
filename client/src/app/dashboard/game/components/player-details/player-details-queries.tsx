import { api } from "@/app/clients/api-client";
import {
	BuyInProps,
	CashOutProps,
	PlayerChangeProps,
} from "@/app/dashboard/game/components/player-details/types";
import { GameProps } from "@/app/dashboard/games/types";
import { useMutation } from "@tanstack/react-query";

export const useAddPlayerBuyIn = () => {
	return useMutation<GameProps, unknown, BuyInProps>({
		mutationFn: (vars) =>
			api.putData<PlayerChangeProps, GameProps>(
				`/games/${vars.gameId}/buyin`,
				vars.buyIn
			),
		onSuccess: () => alert("Buy In Updated Successfully!"),
		onError: () => {
			alert("Failed To Updated Buy In");
			throw new Error();
		},
	});
};

export const usePlayerCashOut = () => {
	return useMutation<GameProps, unknown, CashOutProps>({
		mutationFn: (vars) =>
			api.putData<PlayerChangeProps, GameProps>(
				`/games/${vars.gameId}/cashout`,
				vars.cashOut
			),
		onSuccess: () => alert("Cash Out Updated Successfully!"),
		onError: () => {
			alert("Failed To Updated Cash Out");
			throw new Error();
		},
	});
};
