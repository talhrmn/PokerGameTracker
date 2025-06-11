"use client";

import { useAuth } from "@/app/auth/context/context";
import GenericTable from "@/app/dashboard/components/generic-table/generic-table";
import TableDetailsModal from "@/app/dashboard/tables/components/table-details/table-details";

import { TABLE_TABS, tableColumns } from "@/app/dashboard/tables/consts";
import { useFetchTablesQuery } from "@/app/dashboard/tables/tables-queries";
import { Table } from "@/app/dashboard/tables/types";
import { useCallback, useEffect, useMemo, useState } from "react";

export default function TablesPage() {
	const { user } = useAuth();
	const userId = user._id;

	const {
		data: tables = [] as Table[],
		isError: tablesError,
		// isLoading: tablesLoading,
		refetch: refetchTables,
	} = useFetchTablesQuery();

	const [createdTables, setCreatedTables] = useState<Table[]>([]);
	const [invitedTables, setInvitedTables] = useState<Table[]>([]);
	const [activeTab, setActiveTab] = useState<string>(TABLE_TABS.created.key);
	const [selectedTable, setSelectedTable] = useState<Table | null>(null);

	useEffect(() => {
		if (tablesError) {
			console.error("Failed to fetch tables");
			setCreatedTables([]);
			setInvitedTables([]);
		}
	}, [tablesError]);

	useEffect(() => {
		if (!tables || tables.length === 0) {
			setCreatedTables([]);
			setInvitedTables([]);
			return;
		}
		setCreatedTables(tables.filter((t) => t.creator_id === userId));
		setInvitedTables(tables.filter((t) => t.creator_id !== userId));
	}, [tables, userId]);

	const handleRowClick = useCallback((table: Table) => {
		setSelectedTable(table);
	}, []);

	const handleCloseModal = useCallback(() => {
		setSelectedTable(null);
	}, []);

	const handleUpdateTables = useCallback(async () => {
		try {
			await refetchTables();
		} catch (err) {
			console.error("Refetch tables failed", err);
		}
	}, [refetchTables]);

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
					onUpdateTables={handleUpdateTables}
				/>
			)}
		</>
	);
}
