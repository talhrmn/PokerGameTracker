import { Table } from "@/app/dashboard/tables/types";

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
