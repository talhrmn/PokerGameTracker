import { gamesApiClient } from "@/app/clients/games-api-client";
import { tablesApiClient } from "@/app/clients/tables-api-client";
import { TableForm } from "@/app/dashboard/components/poker-table-form/types";
import { GameProps } from "@/app/dashboard/games/types";
import { TableResponseType } from "@/app/dashboard/tables/components/table-details/types";
import { Table } from "@/app/dashboard/tables/types";
import { useMutation } from "@tanstack/react-query";

export const useTableSubmit = (onUpdateTables: () => void) => {
	return useMutation<Table, unknown, { tableId: string; params: TableForm }>({
		mutationFn: (params) => tablesApiClient.updateTable(params),
		onSuccess: () => onUpdateTables(),
		onError: () => alert("Failed to update table"),
	});
};

export const useTableDelete = (
	onUpdateTables: () => void,
	onClose: () => void
) => {
	return useMutation<Table, unknown, string>({
		mutationFn: (tableId) => tablesApiClient.deleteTable(tableId),
		onSuccess: () => {
			onUpdateTables();
			onClose();
		},
		onError: () => alert("Failed to delete table"),
	});
};

export const useGameStart = (
	redirectToGame: (gameId: string) => void,
	onClose: () => void
) => {
	return useMutation<GameProps, unknown, Record<string, unknown>>({
		mutationFn: (params) => gamesApiClient.startGame(params),
		onSuccess: (data) => {
			alert("Game Started Successfully!");
			onClose();
			redirectToGame(data.id);
		},
		onError: () => alert("Failed to start game"),
	});
};

export const useGameResponse = (
	onUpdateTables: () => void,
	onClose: () => void
) => {
	return useMutation<Table, unknown, TableResponseType>({
		mutationFn: (params) => tablesApiClient.reponsedToTableInvite(params),
		onSuccess: () => {
			alert("Game Response Successfully!");
			onUpdateTables();
			onClose();
		},
		onError: () => alert("Failed to responed to game"),
	});
};
