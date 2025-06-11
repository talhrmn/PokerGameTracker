export interface UserStatsType {
  total_profit: number;
  win_rate: number;
  tables_played: number;
  hours_played: number;
}

export interface UserMonthlyStats {
  profit_change: string;
  win_rate_change: string;
  tables_change: string;
  hours_change: string;
}

export interface QuickStat {
  id: number;
  name: string;
  value: string;
  icon: React.ElementType;
  change: string;
  changeType: "increase" | "decrease";
}

export interface QuickStatsProps {
  user_stats: UserStatsType;
  monthly_changes: UserMonthlyStats;
}
