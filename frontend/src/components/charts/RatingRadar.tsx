import React, { useRef, useEffect } from 'react';
import * as echarts from 'echarts';
import { Box } from '@mui/material';
import type { RatingDimension } from '@/types';

interface RatingRadarProps {
  data: RatingDimension[];
  dimensions?: RatingDimension[];
}

const defaultDimensions: RatingDimension[] = [
  { name: '司法风险', score: 0, weight: 0.2, factors: [] },
  { name: '财务健康', score: 0, weight: 0.2, factors: [] },
  { name: '征信状况', score: 0, weight: 0.2, factors: [] },
  { name: '经营稳定性', score: 0, weight: 0.2, factors: [] },
  { name: '股权结构', score: 0, weight: 0.1, factors: [] },
  { name: '合规状况', score: 0, weight: 0.1, factors: [] },
];

const RatingRadar: React.FC<RatingRadarProps> = ({ data, dimensions }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const chartDimensions = (data ?? dimensions ?? defaultDimensions).length > 0
      ? (data ?? dimensions ?? defaultDimensions)
      : defaultDimensions;

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'item',
      },
      radar: {
        indicator: chartDimensions.map((dim) => ({
          name: dim.name,
          max: 100,
        })),
        radius: '60%',
        center: ['50%', '50%'],
        axisName: {
          color: '#666',
          fontSize: 12,
        },
        splitArea: {
          areaStyle: {
            color: ['rgba(21, 101, 192, 0.02)', 'rgba(21, 101, 192, 0.05)'],
          },
        },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: chartDimensions.map((dim) => dim.score),
              name: '评级得分',
              areaStyle: {
                color: 'rgba(21, 101, 192, 0.3)',
              },
              lineStyle: {
                color: '#1565C0',
                width: 2,
              },
              itemStyle: {
                color: '#1565C0',
              },
            },
          ],
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
  }, [data, dimensions]);

  return <Box ref={chartRef} sx={{ width: '100%', height: 400 }} />;
};

export default RatingRadar;
