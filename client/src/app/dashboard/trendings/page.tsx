"use client";

import LineChart from "@/app/dashboard/components/line-chart/line-chart";
import { NivoSeries } from "@/app/dashboard/components/line-chart/types";
import { ChartMetrics } from "@/app/dashboard/trendings/consts";
import styles from "@/app/dashboard/trendings/styles.module.css";
import { useTrendingsQuery } from "@/app/dashboard/trendings/trendings-queries";
import { TrendsProps } from "@/app/dashboard/trendings/types";

const TrendingsPage = () => {
	const { data, isLoading: loading, isError: error } = useTrendingsQuery();

	const colorsList = ["#ff5733", "#33ff57", "#3357ff", "#ff33a8", "#a833ff"];

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
							(user, index) => colorsList[index % colorsList.length]
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

	if (loading) {
		return <div className={styles.loading}>Loading statistics...</div>;
	}

	if (error) {
		return <div className={styles.error}>Error loading data: {error}</div>;
	}

	return (
		<div className={styles.container}>
			<h1 className={styles.title}>Game Trends Over Time</h1>

			{/* Summary Stats Cards */}
			<div className={styles.statsGrid}>
				<div className={styles.statCard}>
					<h3>Average Pot Size </h3>
					<div className={styles.statValue}>
						{data?.average_pot_size.toFixed(1) || "0"}
					</div>
				</div>
				<div className={styles.statCard}>
					<h3>Average Win Rate</h3>
					<div className={styles.statValue}>
						{((data?.average_win_rate || 0) * 100).toFixed(1) || "0.0"}%
					</div>
				</div>
				<div className={styles.statCard}>
					<h3>Average Hours Per Game</h3>
					<div className={styles.statValue}>
						{data?.average_hours_played.toFixed(1) || "0.0"}
					</div>
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
		</div>
	);
};

export default TrendingsPage;
