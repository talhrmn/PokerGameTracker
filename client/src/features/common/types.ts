import { Table } from "@/features/dashboard/table/types/tables.types";
import { LucideIcon } from "lucide-react";
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
  
  export interface TableGameFormProps {
    name: string;
    venue: string;
    scheduled_date: string;
    scheduled_time: string;
    minimum_buy_in: number;
    maximum_players: number;
    game_type: string;
    blind_structure: string;
    description: string;
    date?: string;
  }

export interface FormAction {
  id: string;
  label: string;
  icon?: LucideIcon;
  onClick?: () => void;
  type?: 'button' | 'submit';
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  disabled?: boolean;
  loading?: boolean;
  loadingText?: string;
}

export interface TableFormProps {
  title: string;
  initialData: TableGameFormProps;
  onSubmit: (data: TableGameFormProps) => void;
  onClose: () => void;
  actions: FormAction[];
  disabled?: boolean;
  loading?: boolean;
}

export interface ActionButtonProps {
  action: FormAction;
  globalLoading?: boolean;
}

export interface TableDetailsModalProps {
  table: Table;
  isCreator: boolean;
  onClose: () => void;
  onUpdateTables: () => void;
}

export interface TableActionHandlers {
  onDelete: () => void;
  onStartGame: () => void;
  onJoinGame: () => void;
  onDeclineGame: () => void;
  onViewPlayers: () => void;
  onGoToGame: () => void;
  onInvite: () => void;
}
