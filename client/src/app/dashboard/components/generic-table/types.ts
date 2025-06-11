import { ReactNode } from "react";

export interface ColumnDefinition<T> {
	key: string;
	header: string;
	render?: (item: T) => ReactNode;
	icon?: React.ComponentType<{ className?: string }>;
	className?: string;
	hidden?: boolean;
	align?: "left" | "right";
	tooltip?: string | ((item: T) => string);
}

interface TabDefinition {
	key: string;
	label: string;
}

export interface PaginationOptions {
	currentPage: number;
	totalPages: number;
	totalItems: number;
	itemsPerPage: number;
}

export interface GenericTableProps<T> {
	data: T[];
	columns: ColumnDefinition<T>[];
	title?: string;
	onSearch?: (input: string) => void;
	viewAllLink?: string;
	titleBarColor?: string;
	tabs?: TabDefinition[];
	onRowClick?: (item: T) => void;
	activeTab?: string;
	onTabChange?: (tab: string) => void;
	pagination?: PaginationOptions;
	onPageChange?: (page: number) => void;
}

export type CellValueType = Record<
	string,
	string | number | JSX.Element | undefined
>;
