export interface StatsType {
  total_profit: number;
  games_won: number;
  games_lost: number;
  win_rate: number;
  tables_played: number;
  hours_played: number;
}

export interface MonthlyStatsProps {
  month: string;
  profit: number;
  games_won: number;
  games_lost: number;
  win_rate: number;
  tables_played: number;
  hours_played: number;
}

export interface UserStatsType {
  stats: StatsType;
  monthly_stats: MonthlyStatsProps[];
}
