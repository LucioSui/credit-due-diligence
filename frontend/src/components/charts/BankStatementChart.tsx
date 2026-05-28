import React, { useRef, useEffect } from 'react';
import * as echarts from 'echarts';
import { Box } from '@mui/material';
import type { BankStatementItem } from '@/types';

interface BankStatementChartProps {
  data: BankStatementItem[];
}

const BankStatementChart: React.FC<BankStatementChartProps> = ({ data }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const sortedData = [...data].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
    );

    const dates = sortedData.map((item) => item.date);
    const balances = sortedData.map((item) => item.balance);
    const incomes = sortedData.map((item) => item.income ?? 0);
    const expenses = sortedData.map((item) => item.expense ?? 0);

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        formatter: ((params: any[]) => {
          let result = `${params[0].axisValue}`;
          params.forEach((param) => {
            result += `<br/>${param.seriesName}: ${param.value}`;
          });
          return result;
        }) as any,
      },
      legend: {
        data: ['余额', '收入', '支出'],
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
        data: dates,
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: 'value',
        name: '金额',
      },
      series: [
        {
          name: '余额',
          type: 'line',
          data: balances,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(21, 101, 192, 0.3)',
              },
              {
                offset: 1,
                color: 'rgba(21, 101, 192, 0.05)',
              },
            ]),
          },
          itemStyle: {
            color: '#1565C0',
          },
          smooth: true,
        },
        {
          name: '收入',
          type: 'bar',
          data: incomes,
          itemStyle: {
            color: '#4CAF50',
          },
          stack: 'total',
        },
        {
          name: '支出',
          type: 'bar',
          data: expenses.map((v) => -v),
          itemStyle: {
            color: '#F44336',
          },
          stack: 'total',
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

export default BankStatementChart;
