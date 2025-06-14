import { GameStats } from "@/features/dashboard/game/types/games.types";
import {
	UserMonthlyStats,
	UserStatsType,
} from "@/features/dashboard/main/types/quick-stats.types";

export interface DashboardStatsType {
	recent_games: GameStats[];
	user_stats: UserStatsType;
	monthly_changes: UserMonthlyStats;
}
