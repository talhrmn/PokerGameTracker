"use client";

import { useAuth } from "@/app/auth/context/context";
import GenericTable from "@/app/dashboard/components/generic-table/generic-table";
import TableDetailsModal from "@/app/dashboard/tables/components/table-details/table-details";

import { apiClient } from "@/app/clients/api-client";
import { TABLE_TABS, tableColumns } from "@/app/dashboard/tables/consts";
import { Table } from "@/app/dashboard/tables/types";
import { useCallback, useEffect, useMemo, useState } from "react";

export default function TablesPage() {
	const { user } = useAuth();
	const [createdTables, setCreatedTables] = useState<Table[]>([]);
	const [invitedTables, setInvitedTables] = useState<Table[]>([]);
	const [activeTab, setActiveTab] = useState<string>(TABLE_TABS.created.key);
	const [selectedTable, setSelectedTable] = useState<Table | null>(null);

	const fetchTables = useCallback(async () => {
		try {
			const response = await apiClient.get("/tables");
			const tables = response.data;
			const userId = user._id;
			setCreatedTables(
				tables.filter((table: Table) => table.creator_id === userId)
			);
			setInvitedTables(
				tables.filter((table: Table) => table.creator_id !== userId)
			);
		} catch (error) {
			console.error("Failed to fetch tables", error);
		}
	}, [user]);

	useEffect(() => {
		fetchTables();
	}, [user, fetchTables]);

	const handleRowClick = (table: Table) => {
		setSelectedTable(table);
	};

	const handleCloseModal = () => {
		setSelectedTable(null);
	};

	const tableData = useMemo(() => {
		return activeTab === TABLE_TABS.created.key ? createdTables : invitedTables;
	}, [activeTab, createdTables, invitedTables]);

	return (
		<>
			<GenericTable
				data={tableData}
				columns={tableColumns}
				title="My Tables"
				tabs={Object.values(TABLE_TABS)}
				activeTab={activeTab}
				onTabChange={(tab) => setActiveTab(tab)}
				onRowClick={handleRowClick}
				titleBarColor="#f56565"
			/>

			{selectedTable && (
				<TableDetailsModal
					table={selectedTable}
					isCreator={activeTab === TABLE_TABS.created.key}
					onClose={handleCloseModal}
					onUpdateTables={fetchTables}
				/>
			)}
		</>
	);
}
