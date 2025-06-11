import { tablesApiClient } from "@/app/clients/tables-api-client";
import { useQuery } from "@tanstack/react-query";

export const useGameTableQuery = (table_id: string) => {
	return useQuery({
		queryKey: ["game-details"],
		queryFn: () => tablesApiClient.getTable(table_id),
	});
};
