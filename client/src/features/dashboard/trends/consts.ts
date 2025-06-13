import { ChartProps } from "@/features/common/types";

export const ChartMetrics: Record<string, ChartProps> = {
  players_trend: {
    label: "Number of Players",
    colors: ["#3182CE"],
    xAxisLable: "Table Name",
    yAxisLable: "# of Players",
    renderTooltip: (value) => value.toString(),
  },
  pot_trend: {
    label: "Total Pot Size",
    colors: ["#38A169"],
    xAxisLable: "Table Name",
    yAxisLable: "Pot Size ($)",
    renderTooltip: (value) => `$${value.toFixed(2)}`,
  },
  duration_trend: {
    label: "Game Duration",
    colors: ["#DD6B20"],
    xAxisLable: "Table Name",
    yAxisLable: "Time in Hours",
    renderTooltip: (value) => `${value.toFixed(1)} hrs`,
  },
  profit_trend: {
    label: "Profet Per User",
    colors: [],
    xAxisLable: "Table Name",
    yAxisLable: "Profit per User ($)",
    renderTooltip: (value) => `$${value.toFixed(2)}`,
  },
  buy_in_trend: {
    label: "Buy-ins Per User",
    colors: [],
    xAxisLable: "Table Name",
    yAxisLable: "Buy In per User",
    renderTooltip: (value) => `$${value.toFixed(2)}`,
  },
};

export const COLORS_LIST = ["#ff5733", "#33ff57", "#3357ff", "#ff33a8", "#a833ff"];
