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

export interface NivoDataPointProps {
    x: string;
    y: number;
  }
  
  export interface NivoSeries {
    id: string;
    colors?: string[];
    data: NivoDataPointProps[];
  }
  
  export interface ChartProps {
    label: string;
    colors: string[];
    xAxisLable?: string;
    yAxisLable: string;
    renderTooltip: (value: number) => string;
  }
  
  export interface LineChartProps extends ChartProps {
    data: NivoSeries[];
  }
  
  export interface TableForm {
    name: string;
    venue: string;
    scheduled_date: string;
    scheduled_time: string;
    minimum_buy_in: number;
    maximum_players: number;
    game_type: "Texas Hold'em";
    blind_structure: "1/2";
    description: string;
    date?: string;
  }
  
  export interface PokerTableFormProps {
    formTitle: string;
    initialData: TableForm;
    handleFormSubmit: (params: TableForm) => void;
    onClose: () => void;
    formActions: JSX.Element;
    editDisabled: boolean;
  }
  