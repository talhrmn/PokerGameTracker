import styles from "@/app/dashboard/main/components/quick-stats/styles.module.css";
import {
	QuickStat,
	QuickStatsProps,
} from "@/app/dashboard/main/components/quick-stats/types";
import { Clock, DollarSign, Table, Trophy } from "lucide-react";

export default function QuickStats({
	user_stats,
	monthly_changes,
}: QuickStatsProps) {
	const getChangeType = (change: string) =>
		change.startsWith("+") ? "increase" : "decrease";

	const stats = [
		{
			id: 1,
			name: "Total Profit",
			value: `$${Math.round(user_stats.total_profit || 0)}`,
			icon: DollarSign,
			change: monthly_changes.profit_change || "",
			changeType: getChangeType(monthly_changes.profit_change),
		},
		{
			id: 2,
			name: "Win Rate",
			value: `${Math.round((user_stats.win_rate || 0) * 100)}%`,
			icon: Trophy,
			change: monthly_changes.win_rate_change || "",
			changeType: getChangeType(monthly_changes.win_rate_change),
		},
		{
			id: 3,
			name: "Tables Played",
			value: `${user_stats.tables_played}`,
			icon: Table,
			change: monthly_changes.tables_change || "",
			changeType: getChangeType(monthly_changes.tables_change),
		},
		{
			id: 4,
			name: "Hours Played",
			value: `${Math.round(user_stats.hours_played || 0)}`,
			icon: Clock,
			change: monthly_changes.hours_change || "",
			changeType: getChangeType(monthly_changes.hours_change),
		},
	] as QuickStat[];

	return (
		<div className={styles.statsGrid}>
			{stats.map((stat) => (
				<div key={stat.id} className={styles.statCard}>
					<div className={styles.statHeader}>
						<div className={styles.iconContainer}>
							<stat.icon className={styles.icon} />
						</div>
						<div className={styles.statInfo}>
							<dl>
								<dt className={styles.statName}>{stat.name}</dt>
								<dd>
									<div className={styles.statValue}>{stat.value}</div>
								</dd>
							</dl>
						</div>
					</div>
					<div
						className={`${styles.changeIndicator} ${
							stat.changeType === "increase" ? styles.increase : styles.decrease
						}`}
					>
						<span className={styles.changeValue}>{stat.change}</span>
						<span className={styles.changeLabel}>from last month</span>
					</div>
				</div>
			))}
		</div>
	);
}
