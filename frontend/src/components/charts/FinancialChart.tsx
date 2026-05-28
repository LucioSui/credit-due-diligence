import React, { useRef, useEffect } from 'react';
import * as echarts from 'echarts';
import { Box } from '@mui/material';
import type { FinancialIndicator } from '@/types';

interface FinancialChartProps {
  data: FinancialIndicator[];
}

const FinancialChart: React.FC<FinancialChartProps> = ({ data }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const sortedData = [...data].sort((a, b) => a.year - b.year);
    const years = sortedData.map((item) => item.year);

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
      },
      legend: {
        data: ['营业收入', '净利润', 'ROE', '资产负债率'],
        bottom: 0,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '10%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: years,
        axisLabel: {
          formatter: '{value}年',
        },
      },
      yAxis: [
        {
          type: 'value',
          name: '金额 (万元)',
          position: 'left',
        },
        {
          type: 'value',
          name: '比率 (%)',
          position: 'right',
          axisLabel: {
            formatter: '{value}%',
          },
        },
      ],
      series: [
        {
          name: '营业收入',
          type: 'bar',
          data: sortedData.map((item) => item.revenue ?? 0),
          itemStyle: {
            color: '#1976D2',
          },
        },
        {
          name: '净利润',
          type: 'bar',
          data: sortedData.map((item) => item.net_profit ?? 0),
          itemStyle: {
            color: '#4CAF50',
          },
        },
        {
          name: 'ROE',
          type: 'line',
          yAxisIndex: 1,
          data: sortedData.map((item) => (item.roe ?? 0) * 100),
          itemStyle: {
            color: '#FF9800',
          },
          smooth: true,
        },
        {
          name: '资产负债率',
          type: 'line',
          yAxisIndex: 1,
          data: sortedData.map((item) => (item.asset_liability_ratio ?? 0) * 100),
          itemStyle: {
            color: '#F44336',
          },
          smooth: true,
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
  }, [data]);

  return <Box ref={chartRef} sx={{ width: '100%', height: 400 }} />;
};

export default FinancialChart;
