"use client";

import LineChart from "@/features/common/components/line-chart/line-chart";
import { NivoSeries } from "@/features/common/types";
import { ChartMetrics, COLORS_LIST } from "@/features/dashboard/trends/consts";
import { useTrendingsQuery } from "@/features/dashboard/trends/hooks/trendings.queries";
import { TrendsProps } from "@/features/dashboard/trends/types";
import styles from "./styles.module.css";
import commonStyles from "@/features/common/styles.module.css";

const TrendingsPage = () => {
	const { data, isLoading, isError } = useTrendingsQuery();

	if (isLoading) {
		return (
			<div className={commonStyles.loadingContainer}>
				<div className={commonStyles.loadingSpinner}></div>
				<p>Loading table data...</p>
			</div>
		);
	}

	if (isError)
		return <div className={styles.error}>Error loading data: {isError}</div>;

	const avgPotSize = data?.average_pot_size.toFixed(1) || "0";

	const avgWinRate = (data?.average_win_rate || 0) * 100;

	const avgDuration = data?.average_hours_played.toFixed(1) || "0.0";

	const lineChartData = !data
		? []
		: (Object.keys(ChartMetrics) as Array<keyof TrendsProps>)
				.filter(
					(metric) =>
						typeof data[metric] === "object" && !Array.isArray(data[metric])
				)
				.map((metric) => {
					const metricData = data[metric];
					const isNestedRecord = Object.values(metricData).some(
						(value) => typeof value === "object"
					);

					let seriesData: NivoSeries[];

					if (isNestedRecord) {
						const users = new Set<string>();
						Object.values(
							metricData as Record<string, Record<string, number>>
						).forEach((entry) => {
							Object.keys(entry).forEach((user) => users.add(user));
						});

						ChartMetrics[metric].colors = Array.from(users).map(
							(user, index) => COLORS_LIST[index % COLORS_LIST.length]
						);
						seriesData = Array.from(users).map((user) => ({
							id: user,
							colors: ChartMetrics[metric].colors,
							data: Object.entries(
								metricData as Record<string, Record<string, number>>
							)
								.map(([x, yValues]) => ({
									x,
									y: yValues[user] ?? 0,
								}))
								.filter((point) => point.y !== undefined),
						}));
					} else {
						seriesData = [
							{
								id: ChartMetrics[metric].label,
								colors: ChartMetrics[metric].colors,
								data: Object.entries(metricData as Record<string, number>).map(
									([key, value]) => ({
										x: key,
										y: value,
									})
								),
							},
						];
					}

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
			{/* Summary Stats Cards */}
			<div className={styles.statsGrid}>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Pot Size </h3>
					<div className={styles.statValueBase}>{avgPotSize}</div>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Win Rate</h3>
					<div
						className={`${styles.statValueBase} ${
							avgWinRate >= 0
								? styles.statValuePositive
								: styles.statValueNegative
						}`}
					>
						{avgWinRate.toFixed(1) || "0.0"}%
					</div>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Hours Per Game</h3>
					<div className={styles.statValueBase}>{avgDuration}</div>
				</div>
			</div>

			<div className={styles.chartsGrid}>
				{lineChartData &&
					lineChartData.map((item, index) => (
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

export default TrendingsPage;
