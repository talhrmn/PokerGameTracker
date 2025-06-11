import { tablesApiClient } from "@/app/clients/tables-api-client";
import { TableForm } from "@/app/dashboard/components/poker-table-form/types";
import { Table } from "@/app/dashboard/tables/types";
import { useMutation } from "@tanstack/react-query";

export const useCreateTable = () => {
	return useMutation<Table, unknown, TableForm>({
		mutationFn: (params) => tablesApiClient.createTable(params),
		onSuccess: () => alert("Table Created Successfully!"),
		onError: () => alert("Table Creation Failed"),
	});
};
