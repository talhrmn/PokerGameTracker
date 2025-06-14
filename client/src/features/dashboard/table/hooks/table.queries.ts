import { TableGameFormProps } from "@/features/common/types";
import { gameService } from "@/features/dashboard/game/services/game.service";
import { GameProps } from "@/features/dashboard/game/types/games.types";
import { tableService } from "@/features/dashboard/table/services/table.service";
import { TableResponseType } from "@/features/dashboard/table/types/table-detail.types";
import { SendInviteType } from "@/features/dashboard/table/types/table-invite.types";
import { Table, TablesData } from "@/features/dashboard/table/types/tables.types";
import { useMutation, useQuery } from "@tanstack/react-query";


export const useFetchTablesQuery = (activeTab: string, limit: number, skip: number	) => {
	return useQuery<TablesData, unknown>({
		queryKey: ["tables", activeTab, limit, skip],
		queryFn: () => tableService.getTables(activeTab, limit, skip),
		staleTime: 5 * 60 * 1000,
	});
};


export const useTableSubmit = (onUpdateTables: () => void) => {
	return useMutation<Table, unknown, { tableId: string; params: TableGameFormProps }>({
		mutationFn: (params) => tableService.updateTable(params),
		onSuccess: () => onUpdateTables(),
		onError: () => alert("Failed to update table"),
	});
};

export const useCreateTable = () => {
	return useMutation<Table, unknown, TableGameFormProps>({
		mutationFn: (params) => tableService.createTable(params),
		onSuccess: () => alert("Table Created Successfully!"),
		onError: () => alert("Table Creation Failed"),
	});
};

export const useTableDelete = (
	onUpdateTables: () => void,
	onClose: () => void
) => {
	return useMutation<Table, unknown, string>({
		mutationFn: (tableId) => tableService.deleteTable(tableId),
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
		mutationFn: (params) => gameService.startGame(params),
		onSuccess: (data) => {
			alert("Game Started Successfully!");
			onClose();
			redirectToGame(data._id);
		},
		onError: () => alert("Failed to start game"),
	});
};

export const useGameTableQuery = (table_id: string) => {
	return useQuery({
		queryKey: ["game-details", table_id],
		queryFn: () => tableService.getTable(table_id),
	});
};

export const useGameResponse = (
	onUpdateTables: () => void,
	onClose: () => void
) => {
	return useMutation<Table, unknown, TableResponseType>({
		mutationFn: (params) => tableService.reponsedToTableInvite(params),
		onSuccess: () => {
			alert("Game Response Successfully!");
			onUpdateTables();
			onClose();
		},
		onError: () => alert("Failed to responed to game"),
	});
};

export const useSendInvite = () => {
	return useMutation<Table, unknown, SendInviteType>({
		mutationFn: (params) => tableService.sendTableInvite(params),
		onSuccess: () => alert("Invites Sent Successfully!"),
		onError: () => alert("Failed to send invitation"),
	});
};
