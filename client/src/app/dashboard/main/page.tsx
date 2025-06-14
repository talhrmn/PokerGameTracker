"use client";

import QuickAccessCards from "@/features/dashboard/main/components/quick-access-cards/quick-access-cards";
import QuickStats from "@/features/dashboard/main/components/quick-stats/quick-stats";
import RecentGames from "@/features/dashboard/main/components/recent-games/recent-games";
import { DASHBOARD_STATS_DEFAULT } from "@/features/dashboard/main/consts";
import { ACCESS_CARDS } from "@/features/dashboard/main/consts/quic-access-cards.consts";
import { useFetchDashStatsQuery } from "@/features/dashboard/statistics/hooks/statistics.queries";
import styles from "./styles.module.css";

const Main = () => {
	const {
		data: dashboardStats = DASHBOARD_STATS_DEFAULT,
		isLoading,
		// isError,
	} = useFetchDashStatsQuery();

	return (
		<>
			<main className={styles.mainContent}>
				<div className={styles.quickStatsSection}>
					<QuickStats
						user_stats={dashboardStats.user_stats}
						monthly_changes={dashboardStats.monthly_changes}
					/>
				</div>
				<div className={styles.recentGamesSection}>
					<RecentGames
						recentGames={dashboardStats.recent_games}
						isLoading={isLoading}
					/>
				</div>

				<div className={styles.quickAccessSection}>
					<QuickAccessCards cards={ACCESS_CARDS} />
				</div>
			</main>
		</>
	);
};

export default Main;
