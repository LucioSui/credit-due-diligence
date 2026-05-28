import React, { useRef, useEffect } from 'react';
import * as echarts from 'echarts';
import { Box } from '@mui/material';
import type { EquityNode } from '@/types';

interface EquityTreeChartProps {
  data: EquityNode[];
}

interface TreeNodeData {
  name: string;
  value?: number;
  itemStyle?: { color: string };
  children?: TreeNodeData[];
}

function transformEquityNodes(nodes: EquityNode[]): TreeNodeData[] {
  const transformNode = (node: EquityNode): TreeNodeData => {
    const children = node.children?.map(transformNode) ?? [];
    return {
      name: node.name,
      value: node.share_ratio,
      itemStyle: {
        color: node.entity_type === 'person' ? '#4CAF50' : '#1976D2',
      },
      children,
    };
  };

  return nodes.map(transformNode);
}

const EquityTreeChart: React.FC<EquityTreeChartProps> = ({ data }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const rootNode: TreeNodeData = {
      name: '股权穿透图',
      children: transformEquityNodes(data),
    };

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            const d = params.data as TreeNodeData;
            return `${d.name}<br/>持股比例: ${(d.value ?? 0).toFixed(1)}%`;
          }
          return '';
        },
      },
      series: {
        type: 'tree',
        data: [rootNode],
        top: '5%',
        left: '10%',
        bottom: '5%',
        right: '10%',
        symbolSize: 7,
        label: {
          position: 'top',
          verticalAlign: 'middle',
          align: 'center',
          fontSize: 12,
        },
        leaves: {
          label: {
            position: 'bottom',
            verticalAlign: 'middle',
            align: 'center',
          },
        },
        emphasis: {
          focus: 'descendant',
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750,
        layout: 'orthogonal',
        orient: 'LR',
        lineStyle: {
          color: '#ccc',
          width: 2,
          curveness: 0.5,
        },
      },
    };

    chartInstance.current.setOption(option);

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

export default EquityTreeChart;
