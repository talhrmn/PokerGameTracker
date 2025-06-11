export interface NivoDataPointProps {
  x: string;
  y: number;
}

export interface NivoSeries {
  id: string;
  colors?: string[];
  data: NivoDataPointProps[];
}

export interface ChartProps {
  label: string;
  colors: string[];
  xAxisLable?: string;
  yAxisLable: string;
  renderTooltip: (value: number) => string;
}

export interface LineChartProps extends ChartProps {
  data: NivoSeries[];
}
