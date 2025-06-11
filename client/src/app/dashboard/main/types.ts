import { GameStats } from "@/app/dashboard/games/types";
import {
	UserMonthlyStats,
	UserStatsType,
} from "@/app/dashboard/main/components/quick-stats/types";

export interface DashboardStatsType {
	recent_games: GameStats[];
	user_stats: UserStatsType;
	monthly_changes: UserMonthlyStats;
}
