import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import EquityTreeChart from '@/components/charts/EquityTreeChart';
import DataCard from '@/components/common/DataCard';
import { getEquityStructure, getActualController } from '@/api/equity';
import type { EquityStructure, EquityNode } from '@/types';

interface EquityTabProps {
  companyId: string;
}

/** Recursively count the max depth of the equity tree */
const calcDepth = (nodes: EquityNode[]): number => {
  if (!nodes || nodes.length === 0) return 0;
  let max = 0;
  for (const node of nodes) {
    const childDepth = node.children ? calcDepth(node.children) : 0;
    max = Math.max(max, 1 + childDepth);
  }
  return max;
};

const EquityTab: React.FC<EquityTabProps> = ({ companyId }) => {
  const [structure, setStructure] = useState<EquityStructure | null>(null);
  const [controller, setController] = useState<EquityNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    (async () => {
      try {
        const [structRes, ctrlRes] = await Promise.all([
          getEquityStructure(companyId),
          getActualController(companyId),
        ]);
        setStructure(structRes.data || null);
        setController(ctrlRes.data || structRes.data?.actual_controller || null);
      } catch {
        setError('获取股权穿透数据失败');
      } finally {
        setLoading(false);
      }
    })();
  }, [companyId]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
        <CircularProgress />
      </Box>
    );
  }

  const depth = structure ? calcDepth(structure.shareholders) : 0;
  const shareholders = structure?.shareholders || [];

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>
      )}

      {/* Equity Tree Chart */}
      <Box sx={{ mb: 4, minHeight: 400, border: '1px solid #e0e0e0', borderRadius: 1, p: 1 }}>
        <EquityTreeChart data={shareholders} />
      </Box>

      {/* Below chart sections */}
      <Grid container spacing={3}>
        {/* Shareholders / Beneficial owners */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
            受益所有人
          </Typography>
          <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>姓名</TableCell>
                  <TableCell>持股比例</TableCell>
                  <TableCell>类型</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {shareholders.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
                  </TableRow>
                ) : (
                  shareholders.map((node, i) => (
                    <TableRow key={node.id || i}>
                      <TableCell>{node.name}</TableCell>
                      <TableCell>{node.share_ratio != null ? `${node.share_ratio}%` : '-'}</TableCell>
                      <TableCell>{node.entity_type === 'person' ? '自然人' : '企业'}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>

        {/* Actual controller + Depth */}
        <Grid item xs={12} md={6}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                实际控制人
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, boxShadow: 0 }}>
                {controller ? (
                  <Box>
                    <Typography variant="body1" fontWeight={600}>
                      {controller.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      类型：{controller.entity_type === 'person' ? '自然人' : '企业'}
                      {controller.share_ratio != null && ` | 持股比例：${controller.share_ratio}%`}
                    </Typography>
                  </Box>
                ) : (
                  <Typography color="text.secondary">暂无数据</Typography>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <DataCard title="穿透层数" value={String(depth)} />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EquityTab;
