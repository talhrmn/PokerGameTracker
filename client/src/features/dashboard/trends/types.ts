export interface TrendsProps {
  average_pot_size: number;
  average_win_rate: number;
  average_hours_played: number;
  average_num_of_players: number;
  pot_trend: Record<string, number>;
  players_trend: Record<string, number>;
  duration_trend: Record<string, number>;
  profit_trend: Record<string, Record<string, number>>;
  buy_in_trend: Record<string, Record<string, number>>;
}
