import { ChartProps } from "@/features/common/types";


export const ChartMetrics: Record<string, ChartProps> = {
  profit: {
    label: "Profit",
    colors: ["#3182CE"],
    xAxisLable: "Month",
    yAxisLable: "Profit ($)",
    renderTooltip: (value) => `$${value.toFixed(2)}`,
  },
  win_rate: {
    label: "Win Rate",
    colors: ["#38A169"],
    xAxisLable: "Month",
    yAxisLable: "Win Rate (%)",
    renderTooltip: (value) => `${value}%`,
  },
  tables_played: {
    label: "Tables Played",
    colors: ["#DD6B20"],
    xAxisLable: "Month",
    yAxisLable: "Tables",
    renderTooltip: (value) => value.toString(),
  },
  hours_played: {
    label: "Hours Played",
    colors: ["#805AD5"],
    xAxisLable: "Month",
    yAxisLable: "Hours",
    renderTooltip: (value) => value.toFixed(1),
  },
};
