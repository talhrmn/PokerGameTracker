import { tablesApiClient } from "@/app/clients/tables-api-client";
import { Table } from "@/app/dashboard/tables/types";
import { useQuery } from "@tanstack/react-query";


export const useFetchTablesQuery = () => {
	return useQuery<Table[], unknown>({
		queryKey: ["tables"],
		queryFn: () => tablesApiClient.getTables(),
		staleTime: 5 * 60 * 1000,
	});
};
