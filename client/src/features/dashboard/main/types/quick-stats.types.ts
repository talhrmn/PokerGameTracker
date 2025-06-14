import { StatsType } from "@/features/dashboard/statistics/types";

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
  colorClass: string;
}

export interface QuickStatsProps {
  user_stats: StatsType;
  monthly_changes: UserMonthlyStats;
}
