import { Table } from "@/features/dashboard/table/types/tables.types";

export interface TableDetailsModalProps {
  table: Table;
  isCreator: boolean;
  onClose: () => void;
  onUpdateTables: () => void;
}

export interface TableResponseType {
  tableId: string;
  status: boolean;
}
