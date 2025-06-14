"use client";

import GenericTable from "@/features/common/components/generic-table/generic-table";
import LoadingSpinner from "@/features/common/components/loading-spinner/loading-spinner";
import { TableDetailsModal } from "@/features/dashboard/table/components/table-details/table-details";
import {
	TABLE_TABS,
	tableColumns,
} from "@/features/dashboard/table/consts/tables.consts";
import { useFetchTablesQuery } from "@/features/dashboard/table/hooks/table.queries";
import {
	Table,
	TablesData,
} from "@/features/dashboard/table/types/tables.types";
import { useCallback, useMemo, useState } from "react";

const TablesPage = () => {
	const [activeTab, setActiveTab] = useState<string>(TABLE_TABS.created.key);
	const [currentPage, setCurrentPage] = useState(1);
	const [selectedTable, setSelectedTable] = useState<Table | null>(null);

	const tablesPerPage = 10;

	const skip = useMemo(
		() => (currentPage - 1) * tablesPerPage,
		[currentPage, tablesPerPage]
	);

	const {
		data: tablesData = {} as TablesData,
		isLoading,
		isError: tablesError,
		refetch: refetchTables,
	} = useFetchTablesQuery(activeTab, tablesPerPage, skip);

	const { tables = [], count = 0 } = tablesData;

	if (tablesError) console.error("Failed to fetch tables");

	const handlePageChange = (newPage: number) => {
		setCurrentPage(newPage);
	};

	const handleRowClick = useCallback((table: Table) => {
		setSelectedTable(table);
	}, []);

	const handleCloseModal = useCallback(() => {
		setSelectedTable(null);
	}, []);

	const totalPages = count ? Math.ceil(count / tablesPerPage) : 1;

	const onUpdateTables = () => {
		refetchTables();
		alert("Table updated successfully!");
	};

	if (isLoading) {
		return <LoadingSpinner message="Loading tables data..." />;
	}

	return (
		<>
			<GenericTable
				data={tables}
				columns={tableColumns}
				title="My Tables"
				tabs={Object.values(TABLE_TABS)}
				activeTab={activeTab}
				onTabChange={(tab) => {
					setActiveTab(tab);
					setCurrentPage(1);
				}}
				onRowClick={handleRowClick}
				titleBarColor="#f56565"
				pagination={{
					currentPage,
					totalPages,
					totalItems: count || 1,
					itemsPerPage: tablesPerPage,
				}}
				onPageChange={handlePageChange}
			/>

			{selectedTable && (
				<TableDetailsModal
					table={selectedTable}
					isCreator={activeTab === TABLE_TABS.created.key}
					onClose={handleCloseModal}
					onUpdateTables={onUpdateTables}
				/>
			)}
		</>
	);
};

export default TablesPage;
