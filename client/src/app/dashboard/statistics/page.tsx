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

	if (loading)
		return <div className={styles.loading}>Loading statistics...</div>;
	if (error)
		return <div className={styles.error}>Error loading data: {error}</div>;

	const totalProfit = data.reduce(
		(sum: number, item: { profit: number }) => sum + item.profit,
		0
	);

	const avgWinRate =
		(data.reduce(
			(sum: number, item: { win_rate: number }) => sum + item.win_rate,
			0
		) /
			(data.length || 1)) *
		100;

	const totalTables = data.reduce(
		(sum: number, item: { tables_played: number }) => sum + item.tables_played,
		0
	);

	const totalDuration = data
		.reduce(
			(sum: number, item: { hours_played: number }) => sum + item.hours_played,
			0
		)
		.toFixed(1);

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

	return (
		<div className={styles.statsContainer}>
			<h1 className={styles.title}>Statistics Over Time</h1>
			{/* Summary Cards */}
			<div className={styles.statsGrid}>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Total Profit</h3>
					<p
						className={`${styles.statValueBase} ${
							totalProfit >= 0
								? styles.statValuePositive
								: styles.statValueNegative
						}`}
					>
						{}${totalProfit.toFixed(2)}
					</p>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Average Win Rate</h3>
					<p
						className={`${styles.statValueBase} ${
							avgWinRate >= 0.5
								? styles.statValuePositive
								: styles.statValueNegative
						}`}
					>
						{avgWinRate.toFixed(1)}%
					</p>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Total Tables</h3>
					<p className={styles.statValueBase}>{totalTables}</p>
				</div>
				<div className={styles.statCard}>
					<h3 className={styles.statTitle}>Total Hours</h3>
					<p className={styles.statValueBase}>{totalDuration}</p>
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
};

export default StatisticsPage;
