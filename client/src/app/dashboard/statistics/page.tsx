"use client";

import styles from "@/app/dashboard/statistics/styles.module.css";
import { MonthlyStatsProps } from "@/app/dashboard/statistics/types";

import LineChart from "@/app/dashboard/components/line-chart/line-chart";
import { NivoSeries } from "@/app/dashboard/components/line-chart/types";
import { ChartMetrics } from "@/app/dashboard/statistics/consts";
import { useFetchStats } from "@/app/dashboard/statistics/statistics-queries";

const StatisticsPage = () => {
	const {
		data = [] as MonthlyStatsProps[],
		isLoading: loading,
		isError: error,
	} = useFetchStats();

	const loadingLabel = (
		<div className={styles.loading}>Loading statistics...</div>
	);

	const errorLabel = (
		<div className={styles.error}>Error loading data: {error}</div>
	);

	const lineChartData =
		!data || data.length === 0
			? []
			: Object.keys(ChartMetrics).map((metric) => {
					const seriesData: NivoSeries[] = [
						{
							id: ChartMetrics[metric].label,
							colors: ChartMetrics[metric].colors,
							data: data.map((item: MonthlyStatsProps) => ({
								x: item.month,
								y:
									metric === "win_rate"
										? Number(
												(
													(item[metric as keyof MonthlyStatsProps] as number) *
													100
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

	const statsData = (
		<div className={styles.container}>
			<h1 className={styles.title}>Statistics Over Time</h1>

			{/* Summary Cards */}
			<div className={styles.statsGrid}>
				<div className={styles.statCard}>
					<h3>Total Profit</h3>
					<p className={styles.statValue}>
						$
						{data
							.reduce(
								(sum: number, item: { profit: number }) => sum + item.profit,
								0
							)
							.toFixed(2)}
					</p>
				</div>
				<div className={styles.statCard}>
					<h3>Average Win Rate</h3>
					<p className={styles.statValue}>
						{(
							(data.reduce(
								(sum: number, item: { win_rate: number }) =>
									sum + item.win_rate,
								0
							) /
								(data.length || 1)) *
							100
						).toFixed(1)}
						%
					</p>
				</div>
				<div className={styles.statCard}>
					<h3>Total Tables</h3>
					<p className={styles.statValue}>
						{data.reduce(
							(sum: number, item: { tables_played: number }) =>
								sum + item.tables_played,
							0
						)}
					</p>
				</div>
				<div className={styles.statCard}>
					<h3>Total Hours</h3>
					<p className={styles.statValue}>
						{data
							.reduce(
								(sum: number, item: { hours_played: number }) =>
									sum + item.hours_played,
								0
							)
							.toFixed(1)}
					</p>
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
		</div>
	);

	return loading ? loadingLabel : error ? errorLabel : statsData;
};

export default StatisticsPage;
