import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Stack,
  Breadcrumbs,
  Container,
  CircularProgress,
  Alert,
  Snackbar,
  Card,
  CardContent,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import RefreshIcon from '@mui/icons-material/Refresh';
import AppLayout from '@/components/layout/AppLayout';
import RatingBadge from '@/components/common/RatingBadge';
import RatingRadar from '@/components/charts/RatingRadar';
import { getRatingResult, calculateRating } from '@/api/rating';
import { listTasks } from '@/api/tasks';
import type { RatingResult, DueDiligenceTask } from '@/types';
import type { TaskFilters } from '@/types/api';

const RECOMMENDATION_CONFIG: Record<string, { label: string; color: 'success' | 'warning' | 'error' }> = {
  approve: { label: '建议通过', color: 'success' },
  review: { label: '建议复核', color: 'warning' },
  reject: { label: '建议拒绝', color: 'error' },
};

const RatingPage: React.FC = () => {
  const [tasks, setTasks] = useState<DueDiligenceTask[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [ratingResult, setRatingResult] = useState<RatingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Fetch completed tasks for dropdown
  useEffect(() => {
    (async () => {
      try {
        const res = await listTasks({ status: 'completed', page: 1, page_size: 100 } as TaskFilters);
        setTasks(res.data.items);
      } catch {
        setError('获取已完成任务列表失败');
      }
    })();
  }, []);

  // Load rating result when task selected
  const loadRating = async (taskId: string) => {
    if (!taskId) return;
    setLoading(true);
    setError('');
    try {
      const res = await getRatingResult(taskId);
      setRatingResult(res.data);
    } catch {
      setError('获取评级结果失败');
      setRatingResult(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedTaskId) {
      loadRating(selectedTaskId);
    }
  }, [selectedTaskId]);

  const handleRecalculate = async () => {
    if (!selectedTaskId) return;
    setCalculating(true);
    setError('');
    try {
      const res = await calculateRating(selectedTaskId);
      setRatingResult(res.data);
      setSnackbarMessage('评级重新计算成功');
      setSnackbarOpen(true);
    } catch {
      setError('重新计算评级失败');
    } finally {
      setCalculating(false);
    }
  };

  const recommendation = ratingResult ? RECOMMENDATION_CONFIG[ratingResult.recommendation] : null;

  return (
    <AppLayout pageTitle="评级管理">
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 2 }}>
          <Typography
            component="span"
            sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 0.5 }}
            onClick={() => window.history.back()}
          >
            <HomeIcon fontSize="small" /> 首页
          </Typography>
          <Typography color="text.primary" fontWeight={500}>
            评级管理
          </Typography>
        </Breadcrumbs>

        {/* Title + Actions */}
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
          <Typography variant="h5" fontWeight={600}>
            评级管理
          </Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRecalculate}
            disabled={!selectedTaskId || calculating}
          >
            {calculating ? '计算中...' : '重新计算'}
          </Button>
        </Stack>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Task Selector */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <FormControl fullWidth sx={{ minWidth: 300 }}>
            <InputLabel>选择任务</InputLabel>
            <Select
              value={selectedTaskId}
              label="选择任务"
              onChange={(e) => setSelectedTaskId(e.target.value)}
            >
              {tasks.map((task) => (
                <MenuItem key={task.id} value={task.id}>
                  {task.company_name} {task.unified_social_credit_code ? `(${task.unified_social_credit_code})` : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Paper>

        {/* Loading */}
        {loading && !ratingResult && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Rating Content */}
        {!loading && ratingResult && (
          <Stack spacing={3}>
            {/* Overview Cards */}
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Card sx={{ flex: 1 }}>
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2 }}>
                  <RatingBadge grade={ratingResult.grade} />
                  <Box>
                    <Typography variant="body2" color="text.secondary">综合评级</Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {ratingResult.grade} 级
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
              <Card sx={{ flex: 1 }}>
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">综合得分</Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {ratingResult.overall_score.toFixed(1)} / 100
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
              <Card sx={{ flex: 1 }}>
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">授信建议</Typography>
                    <Chip
                      label={recommendation?.label}
                      color={recommendation?.color}
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Stack>

            {/* Radar Chart */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                评级维度雷达图
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <RatingRadar data={ratingResult.dimensions} />
              </Box>
            </Paper>

            {/* Dimension Detail Table */}
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>维度名称</TableCell>
                    <TableCell width={100} align="center">得分</TableCell>
                    <TableCell width={100} align="center">权重</TableCell>
                    <TableCell>评分因子</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {ratingResult.dimensions.map((dim, idx) => (
                    <TableRow key={idx} hover>
                      <TableCell>{dim.name}</TableCell>
                      <TableCell align="center">
                        <Typography
                          fontWeight={600}
                          color={dim.score >= 80 ? 'success.main' : dim.score >= 60 ? 'warning.main' : 'error.main'}
                        >
                          {dim.score.toFixed(1)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">{(dim.weight * 100).toFixed(0)}%</TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
                          {dim.factors.map((factor, fIdx) => (
                            <Chip key={fIdx} label={factor} size="small" variant="outlined" />
                          ))}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Summary */}
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                  评级摘要
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                  {ratingResult.summary}
                </Typography>
              </CardContent>
            </Card>
          </Stack>
        )}

        {/* Empty state */}
        {!loading && !ratingResult && selectedTaskId && (
          <Alert severity="info">该任务暂无评级结果，请点击"重新计算"生成评级。</Alert>
        )}
        {!loading && !ratingResult && !selectedTaskId && (
          <Alert severity="info">请从上方下拉列表选择一个已完成的任务查看评级。</Alert>
        )}
      </Container>

      {/* Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setSnackbarOpen(false)}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </AppLayout>
  );
};

export default RatingPage;
