import { PlayerStatus } from "@/features/dashboard/table/types/tables.types";

export interface Friend {
  user_id: string;
  username: string;
  avatar_url?: string;
}

export interface InviteModalProps {
  tableId: string;
  tableStatus: string;
  isCreator: boolean;
  tableName: string;
  players: PlayerStatus[];
  onClose: () => void;
}

export interface SendInviteType {
  tableId: string;
  params: PlayerStatus[];
}
