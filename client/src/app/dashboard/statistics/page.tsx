"use client";

import {
	MonthlyStatsProps,
	UserStatsType,
} from "@/features/dashboard/statistics/types";
import styles from "./styles.module.css";

import LineChart from "@/features/common/components/line-chart/line-chart";
import LoadingSpinner from "@/features/common/components/loading-spinner/loading-spinner";
import { NivoSeries } from "@/features/common/types";
import { ChartMetrics } from "@/features/dashboard/statistics/consts";
import { useFetchStats } from "@/features/dashboard/statistics/hooks/statistics.queries";

const StatisticsPage = () => {
	const { data = {} as UserStatsType, isLoading, isError } = useFetchStats();

	if (isLoading) {
		return <LoadingSpinner message="Loading statistics..." />;
	}

	if (isError)
		return <div className={styles.error}>Error loading data: {isError}</div>;

	const totalStats = data.stats;
	const monthlyStats = data.monthly_stats;

	const avgProfit = totalStats.total_profit / monthlyStats.length;
	const avgTablesPlayed = totalStats.tables_played / monthlyStats.length;
	const avgHoursPlayed = totalStats.hours_played / monthlyStats.length;

	const lineChartData = Object.keys(ChartMetrics || []).map((metric) => {
		const seriesData: NivoSeries[] = [
			{
				id: ChartMetrics[metric].label,
				colors: ChartMetrics[metric].colors,
				data: monthlyStats.map((item: MonthlyStatsProps) => ({
					x: item.month,
					y:
						metric === "win_rate"
							? Number(
									(
										(item[metric as keyof MonthlyStatsProps] as number) * 100
									).toFixed(1)
							  )
							: Number(item[metric as keyof MonthlyStatsProps]),
				})),
			},
		];

		return {
			label: ChartMetrics[metric].label,
			colors: ChartMetrics[metric].colors,
			xAxisLable: ChartMetrics[metric].xAxisLable,
			yAxisLable: ChartMetrics[metric].yAxisLable,
			renderTooltip: ChartMetrics[metric].renderTooltip,
			data: seriesData,
		};
	});

	return (
		<>
			{/* Summary Cards */}
			<div className={styles.statsGrid}>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Profit</h3>
					<p
						className={`${styles.statValueBase} ${
							avgProfit >= 0
								? styles.statValuePositive
								: styles.statValueNegative
						}`}
					>
						{}${avgProfit.toFixed(1)}
					</p>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Win Rate</h3>
					<p
						className={`${styles.statValueBase} ${
							totalStats.win_rate >= 0.5
								? styles.statValuePositive
								: styles.statValueNegative
						}`}
					>
						{totalStats.win_rate.toFixed(1)}%
					</p>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Tables</h3>
					<p className={styles.statValueBase}>{avgTablesPlayed.toFixed(1)}</p>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Hours</h3>
					<p className={styles.statValueBase}>{avgHoursPlayed.toFixed(2)}h</p>
				</div>
			</div>

			{/* Grid of Charts */}
			<div className={styles.chartsGrid}>
				{lineChartData.map((item, index) => (
					<div key={index} className={styles.chartWrapper}>
						<LineChart
							label={item.label}
							colors={item.colors}
							xAxisLable={item.xAxisLable}
							yAxisLable={item.yAxisLable}
							renderTooltip={item.renderTooltip}
							data={item.data}
						/>
					</div>
				))}
			</div>
		</>
	);
};

export default StatisticsPage;
