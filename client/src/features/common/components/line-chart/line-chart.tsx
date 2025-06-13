import { LineChartProps } from "@/features/common/types";
import { ResponsiveLine } from "@nivo/line";
import React from "react";
import styles from "./styles.module.css";

const LineChart: React.FC<LineChartProps> = ({
	label,
	colors,
	xAxisLable,
	yAxisLable,
	renderTooltip,
	data,
}: LineChartProps) => {
	return (
		<div className={styles.chartContainer}>
			<h3 className={styles.chartTitle}>{label}</h3>
			<div className={styles.chartContent}>
				<ResponsiveLine
					data={data}
					margin={{ top: 30, right: 110, bottom: 50, left: 60 }}
					xScale={{ type: "point" }}
					yScale={{
						type: "linear",
						min: "auto",
						max: "auto",
						stacked: false,
						reverse: false,
					}}
					yFormat={(value) => {
						return renderTooltip(value as number);
					}}
					axisTop={null}
					axisRight={null}
					curve="monotoneX"
					axisBottom={{
						tickSize: 5,
						tickPadding: 10,
						tickRotation: 0,
						legend: xAxisLable,
						legendOffset: 45,
						legendPosition: "middle",
					}}
					axisLeft={{
						tickSize: 5,
						tickPadding: 5,
						tickRotation: 0,
						legend: yAxisLable,
						legendOffset: -42,
						legendPosition: "middle",
						format: (value) => {
							return renderTooltip(value as number);
						},
					}}
					colors={colors}
					enableGridX={true}
					enableGridY={true}
					theme={{
						grid: {
							line: {
								stroke: "black",
								strokeWidth: 1,
								strokeDasharray: "4 4",
							},
						},
						crosshair: {
							line: {
								stroke: colors[0],
								strokeWidth: 1,
								strokeOpacity: 0.35,
							},
						},
						tooltip: {
							container: {
								background: "#1a202c",
								color: "#e2e8f0",
								fontSize: 12,
								borderRadius: 4,
								boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
								padding: "8px 12px",
							},
						},
						axis: {
							legend: {
								text: {
									fontSize: 12,
									fill: "black",
								},
							},
							ticks: {
								text: {
									fontSize: 12,
									fill: "black",
								},
								line: {
									stroke: "#2d3748",
									strokeWidth: 1,
								},
							},
							domain: {
								line: {
									stroke: "#2d3748",
									strokeWidth: 1,
								},
							},
						},
					}}
					pointSize={8}
					pointColor={{ theme: "background" }}
					pointBorderWidth={2}
					pointBorderColor={{ from: "serieColor" }}
					pointLabelYOffset={-12}
					useMesh={true}
					legends={[
						{
							anchor: "bottom-right",
							direction: "column",
							justify: false,
							translateX: 100,
							translateY: 0,
							itemsSpacing: 0,
							itemDirection: "left-to-right",
							itemWidth: 80,
							itemHeight: 20,
							itemOpacity: 0.75,
							symbolSize: 12,
							symbolShape: "circle",
							symbolBorderColor: "rgba(255, 255, 255, 0.5)",
							effects: [
								{
									on: "hover",
									style: {
										itemBackground: "rgba(255, 255, 255, 0.03)",
										itemOpacity: 1,
									},
								},
							],
							itemTextColor: "#a0aec0",
						},
					]}
					tooltip={({ point }) => {
						const data = point.data as { x: string; y: number };
						return (
							<div className={styles.tooltip}>
								<strong>{data.x}</strong>
								<p>
									{point.serieId}: {renderTooltip(data.y)}
								</p>
							</div>
						);
					}}
				/>
			</div>
		</div>
	);
};

export default LineChart;
