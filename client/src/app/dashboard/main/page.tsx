"use client";

import { useAuth } from "@/app/auth/context/context";
import { ACCESS_CARDS } from "@/app/dashboard/main/components/quick-access-cards/consts";
import QuickAccessCards from "@/app/dashboard/main/components/quick-access-cards/quick-access-cards";
import QuickStats from "@/app/dashboard/main/components/quick-stats/quick-stats";
import RecentGames from "@/app/dashboard/main/components/recent-games/recent-games";
import TableCreator from "@/app/dashboard/main/components/table-creator/table-creator";
import { DASHBOARD_STATS_DEFAULT } from "@/app/dashboard/main/consts";
import { useFetchDashStatsQuery } from "@/app/dashboard/main/main-dash-queries";
import styles from "@/app/dashboard/main/styles.module.css";

export default function Main() {
	const { user } = useAuth();

	const {
		data: dashboardStats = DASHBOARD_STATS_DEFAULT,
		// isLoading,
		// isError,
	} = useFetchDashStatsQuery();

	return (
		<>
			<div className={styles.header}>
				<div className={styles.headerContent}>
					<div className={styles.headerLeft}>
						<h2 className={styles.welcomeText}>
							Welcome back, {user.username}!
						</h2>
						<p className={styles.subtitle}>Manage you games</p>
					</div>
					<div className={styles.headerRight}>
						<div className={styles.headerButtons}>
							<TableCreator />
						</div>
					</div>
				</div>
			</div>

			<QuickStats
				user_stats={dashboardStats.user_stats}
				monthly_changes={dashboardStats.monthly_changes}
			/>

			<div className={styles.mainContent}>
				<div className={styles.recentGamesSection}>
					<RecentGames recentGames={dashboardStats.recent_games} />
				</div>

				<div className={styles.quickAccessSection}>
					<QuickAccessCards cards={ACCESS_CARDS} />
				</div>
			</div>
		</>
	);
}
