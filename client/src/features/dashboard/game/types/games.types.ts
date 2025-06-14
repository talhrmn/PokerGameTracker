export type GameStatusEnum = "in_progress" | "completed" | "cancelled";

export interface GameDurationProps {
  hours: number;
  minutes: number;
}

export interface BuyInsProps {
  amount: number;
  time: Date;
}

export interface NotableHandProps {
  hand_id?: string;
  description: string;
  amount_won: number;
}

export interface GamePlayerProps {
  user_id: string;
  username: string;
  buy_ins: BuyInsProps[];
  cash_out: number;
  net_profit: number;
  notable_hands: NotableHandProps[];
}

export interface GameProps {
  _id: string;
  table_id: string;
  creator_id: string;
  status: GameStatusEnum;
  duration: GameDurationProps;
  total_pot: number;
  available_cash_out: number;
  date: Date;
  venue: string;
  players: GamePlayerProps[];
}

export interface GameStats {
  id: number;
  date: string;
  venue: string;
  profit: number;
  players: number;
  duration: string;
  profit_loss: number;
  total_pot: number;
  total_buy_in: number;
}
