import { GameStats } from "@/features/dashboard/game/types/games.types";
import {
	UserMonthlyStats,
} from "@/features/dashboard/main/types/quick-stats.types";
import { StatsType } from "../statistics/types";

export interface DashboardStatsType {
	recent_games: GameStats[];
	user_stats: StatsType;
	monthly_changes: UserMonthlyStats;
}
