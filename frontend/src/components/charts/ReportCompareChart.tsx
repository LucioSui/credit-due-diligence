import React, { useRef, useEffect } from 'react';
import * as echarts from 'echarts';
import { Box } from '@mui/material';

interface ReportItem {
  version: string;
  score: number;
}

interface ReportCompareChartProps {
  reports?: ReportItem[];
  data?: string[];
}

const getScoreColor = (score: number): string => {
  if (score >= 80) return '#4CAF50';
  if (score >= 60) return '#1976D2';
  if (score >= 40) return '#FF9800';
  return '#F44336';
};

const ReportCompareChart: React.FC<ReportCompareChartProps> = ({ reports, data }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    // When data (string[] of report IDs) is passed, convert to ReportItem format
    const reportItems: ReportItem[] = data
      ? data.map((id) => ({ version: id, score: 0 }))
      : (reports ?? []);

    const sortedReports = [...reportItems].sort((a, b) => b.score - a.score);

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter: ((params: any[]) => {
          const param = params[0];
          const d = param.data as [number, string];
          return `${d[1]}<br/>评分: ${d[0]}分`;
        }) as any,
      },
      grid: {
        left: '3%',
        right: '10%',
        bottom: '3%',
        top: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}分',
        },
      },
      yAxis: {
        type: 'category',
        data: sortedReports.map((report) => report.version),
        axisLabel: {
          color: '#666',
        },
      },
      series: [
        {
          type: 'bar',
          data: sortedReports.map((report) => [report.score, report.version]) as any[],
          barWidth: 20,
          itemStyle: {
            color: (params: any) => {
              return getScoreColor(sortedReports[params.dataIndex]?.score ?? 0);
            },
          },
          label: {
            show: true,
            position: 'right',
            formatter: (params: any) => `${params.data[0]}分`,
            color: '#666',
          },
        },
      ],
    };

    chartInstance.current.setOption(option, true);

    const handleResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, [reports, data]);

  return <Box ref={chartRef} sx={{ width: '100%', height: 400 }} />;
};

export default ReportCompareChart;
