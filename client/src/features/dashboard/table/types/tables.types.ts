export interface PlayerStatus {
  user_id: string;
  username: string;
  status: "invited" | "confirmed" | "declined";
}

export interface Table {
  _id: string;
  name: string;
  date: string;
  game_type: string;
  game_id?: string;
  venue: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  players: PlayerStatus[];
  minimum_buy_in: number;
  maximum_players: number;
  creator_id: string;
  blind_structure: string;
  description?: string;
}

export interface TablesData {
  tables: Table[];
  count: number;
}
