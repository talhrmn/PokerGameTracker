"use client";

import { CellValueType, GenericTableProps } from "@/features/common/types";
import {
	ArrowRight,
	ChevronLeft,
	ChevronRight,
	DatabaseBackup,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./styles.module.css";

export default function GenericTable<T>({
	data,
	columns,
	title = "Table",
	onSearch,
	viewAllLink,
	titleBarColor = "#f56565",
	tabs,
	onRowClick,
	activeTab,
	onTabChange,
	pagination,
	onPageChange,
}: GenericTableProps<T>) {
	const [searchTerm, setSearchTerm] = useState<string>("");
	const debounceTimeoutId = useRef<ReturnType<typeof setTimeout> | null>(null);

	const handleSearch = useCallback(
		async (input: string) => {
			if (debounceTimeoutId.current) clearTimeout(debounceTimeoutId.current);
			debounceTimeoutId.current = setTimeout(() => {
				if (onSearch) onSearch(input);
			}, 300);
		},
		[onSearch]
	);

	useEffect(() => {
		return () => {
			if (debounceTimeoutId.current) clearTimeout(debounceTimeoutId.current);
		};
	}, [debounceTimeoutId]);

	const tableData = !data.length ? (
		<div className={styles.emptyTable}>
			<DatabaseBackup className={styles.emptyTableIcon} size={40} />
			<div className={styles.emptyTableText}>No Data to show</div>
		</div>
	) : (
		<table className={styles.table}>
			<thead className={styles.tableHead}>
				<tr>
					{columns.map((column) => (
						<th
							key={column.key}
							scope="col"
							className={`
    ${
			column.key === columns[0].key
				? styles.tableHeadFirstCell
				: styles.tableHeadCell
		}
    ${column.hidden ? styles.tableHeadCellHidden : ""}
    ${column.align === "right" ? styles.tableHeadCellRight : ""}
    ${column.className || ""}
  `}
						>
							{column.header}
						</th>
					))}
				</tr>
			</thead>
			<tbody className={styles.tableBody}>
				{data.map((item, rowIndex) => (
					<tr
						key={rowIndex}
						className={`
${styles.tableRow}
${onRowClick ? styles.clickableRow : ""}
`}
						onClick={() => onRowClick && onRowClick(item)}
					>
						{columns.map((column) => {
							const cellValue = column.render
								? column.render(item)
								: (item as CellValueType)[column.key];

							const tooltipContent =
								column.tooltip &&
								(typeof column.tooltip === "function"
									? column.tooltip(item)
									: column.tooltip);

							let cellInnerContent = cellValue;
							if (column.icon) {
								cellInnerContent = (
									<div className={styles.iconWithText}>
										<column.icon className={styles.icon} />
										{cellValue}
									</div>
								);
							}

							return (
								<td
									key={column.key}
									className={`
${column.key === columns[0].key ? styles.tableFirstCell : styles.tableCell}
${column.hidden ? styles.tableCellHidden : ""}
${column.align === "right" ? styles.tableCellRight : ""}
${column.className || ""}
`}
								>
									{tooltipContent ? (
										<span title={tooltipContent}>{cellInnerContent}</span>
									) : (
										cellInnerContent
									)}
								</td>
							);
						})}
					</tr>
				))}
			</tbody>
		</table>
	);

	const renderPagination = () => {
		if (!pagination) return null;

		const { currentPage, totalPages, totalItems, itemsPerPage } = pagination;

		const startItem = (currentPage - 1) * itemsPerPage + 1;
		const endItem = Math.min(currentPage * itemsPerPage, totalItems);

		return (
			<div className={styles.paginationContainer}>
				<div className={styles.paginationInfo}>
					Showing {totalItems > 0 ? startItem : 0} to {endItem} of {totalItems}{" "}
					items
				</div>

				<div className={styles.paginationControls}>
					<button
						onClick={() => onPageChange && onPageChange(currentPage - 1)}
						disabled={currentPage <= 1}
						className={`${styles.paginationButton} ${
							currentPage <= 1 ? styles.paginationButtonDisabled : ""
						}`}
						aria-label="Previous page"
					>
						<ChevronLeft className={styles.paginationIcon} />
					</button>

					<span className={styles.paginationPageInfo}>
						Page {currentPage} of {totalPages}
					</span>

					<button
						onClick={() => onPageChange && onPageChange(currentPage + 1)}
						disabled={currentPage >= totalPages}
						className={`${styles.paginationButton} ${
							currentPage >= totalPages ? styles.paginationButtonDisabled : ""
						}`}
						aria-label="Next page"
					>
						<ChevronRight className={styles.paginationIcon} />
					</button>
				</div>
			</div>
		);
	};

	const handleTabSwitch = (tabName: string) => {
		if (setSearchTerm) setSearchTerm("");
		if (onTabChange) onTabChange(tabName);
	};

	return (
		<div className={styles.container}>
			<div className={styles.content}>
				{/* Title section */}
				<div className={styles.tablesHeader}>
					<h3 className={styles.title}>
						<span
							className={styles.titleBar}
							style={{ backgroundColor: titleBarColor }}
						></span>
						{title}
					</h3>
					{onSearch && (
						<input
							type="text"
							placeholder="Search Table..."
							value={searchTerm}
							onChange={(e) => {
								setSearchTerm(e.target.value);
								handleSearch(e.target.value);
							}}
							className={styles.searchInput}
						/>
					)}
				</div>

				{/* Tabs navigation */}
				{tabs && (
					<div className={styles.tabsNavigation}>
						{tabs.map((tab) => (
							<button
								key={tab.key}
								className={`
                  ${styles.tabButton}
                  ${activeTab === tab.key ? styles.activeTab : ""}
                `}
								onClick={() => handleTabSwitch(tab.key)}
							>
								{tab.label}
							</button>
						))}
					</div>
				)}

				<div className={styles.tableWrapper}>
					<div className={styles.tableContainer}>{tableData}</div>

					{/* Pagination */}
					{renderPagination()}

					{viewAllLink && !pagination && (
						<div className={styles.viewAllContainer}>
							<Link href={viewAllLink} className={styles.viewAllLink}>
								View all
								<ArrowRight className={styles.viewAllIcon} />
							</Link>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
