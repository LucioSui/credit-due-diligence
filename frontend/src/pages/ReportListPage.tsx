import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  Chip,
  IconButton,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Breadcrumbs,
  Container,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DescriptionIcon from '@mui/icons-material/Description';
import ArticleIcon from '@mui/icons-material/Article';
import AppLayout from '@/components/layout/AppLayout';
import { listTasks } from '@/api/tasks';
import { generateReport, downloadReport } from '@/api/reports';
import type { DueDiligenceTask, ReportMetadata } from '@/types';
import type { TaskFilters } from '@/types/api';

interface ReportWithTask extends ReportMetadata {
  task_id_for_api: string;
}

const STATUS_LABELS: Record<string, string> = {
  draft: '草稿',
  final: '已发布',
};

const STATUS_COLORS: Record<string, 'default' | 'success'> = {
  draft: 'default',
  final: 'success',
};

const ReportListPage: React.FC = () => {
  const navigate = useNavigate();

  const [reports, setReports] = useState<ReportWithTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  // Generate report dialog
  const [generateOpen, setGenerateOpen] = useState(false);
  const [completedTasks, setCompletedTasks] = useState<DueDiligenceTask[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [generating, setGenerating] = useState(false);

  // Load reports: fetch completed tasks and build report entries from them
  const fetchReports = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await listTasks({ status: 'completed', page: page + 1, page_size: pageSize } as TaskFilters);
      const taskItems = res.data.items;
      setTotal(res.data.total);

      // Build report entries from completed tasks with rating results
      const reportEntries: ReportWithTask[] = taskItems
        .filter((t) => t.rating_result)
        .map((t) => ({
          id: `report-${t.id}`,
          task_id: t.id,
          task_id_for_api: t.id,
          company_name: t.company_name,
          generated_at: t.updated_at,
          version: 'v1.0',
          status: 'final' as const,
        }));
      setReports(reportEntries);
    } catch {
      setError('获取报告列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [page, pageSize]);

  // Load completed tasks for generate dialog
  useEffect(() => {
    if (!generateOpen) return;
    (async () => {
      try {
        const res = await listTasks({ status: 'completed', page: 1, page_size: 100 } as TaskFilters);
        setCompletedTasks(res.data.items);
      } catch {
        setError('获取已完成任务失败');
      }
    })();
  }, [generateOpen]);

  const handleGenerateReport = async () => {
    if (!selectedTaskId) {
      setError('请选择一个任务');
      return;
    }
    setGenerating(true);
    setError('');
    try {
      await generateReport(selectedTaskId);
      setGenerateOpen(false);
      setSelectedTaskId('');
      fetchReports();
    } catch {
      setError('生成报告失败');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (report: ReportWithTask, format: 'pdf' | 'docx') => {
    try {
      await downloadReport(report.task_id_for_api, format);
    } catch {
      setError(`下载${format.toUpperCase()}报告失败`);
    }
  };

  return (
    <AppLayout pageTitle="报告中心">
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 2 }}>
          <Typography
            component="span"
            sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 0.5 }}
            onClick={() => navigate('/')}
          >
            <HomeIcon fontSize="small" /> 首页
          </Typography>
          <Typography color="text.primary" fontWeight={500}>
            报告中心
          </Typography>
        </Breadcrumbs>

        {/* Title + Action */}
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
          <Typography variant="h5" fontWeight={600}>
            报告中心
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<ArticleIcon />}
            onClick={() => { setSelectedTaskId(''); setGenerateOpen(true); }}
          >
            生成报告
          </Button>
        </Stack>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {/* Report Table */}
        <TableContainer component={Paper} sx={{ mb: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell width={50}>序号</TableCell>
                <TableCell>企业名称</TableCell>
                <TableCell width={180}>生成时间</TableCell>
                <TableCell width={100}>版本号</TableCell>
                <TableCell width={100}>状态</TableCell>
                <TableCell align="center" width={180}>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports.length === 0 && !loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4, color: '#999' }}>
                    暂无报告数据
                  </TableCell>
                </TableRow>
              ) : (
                reports.map((report, index) => (
                  <TableRow key={report.id} hover>
                    <TableCell>{page * pageSize + index + 1}</TableCell>
                    <TableCell>{report.company_name}</TableCell>
                    <TableCell>{new Date(report.generated_at).toLocaleString('zh-CN')}</TableCell>
                    <TableCell>{report.version}</TableCell>
                    <TableCell>
                      <Chip
                        label={STATUS_LABELS[report.status]}
                        color={STATUS_COLORS[report.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        color="primary"
                        title="预览"
                        onClick={() => navigate(`/reports/${report.id}`)}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        title="下载PDF"
                        onClick={() => handleDownload(report, 'pdf')}
                      >
                        <PictureAsPdfIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="primary"
                        title="下载DOCX"
                        onClick={() => handleDownload(report, 'docx')}
                      >
                        <DescriptionIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={(_, p) => setPage(p)}
          rowsPerPage={pageSize}
          onRowsPerPageChange={(e) => { setPageSize(Number(e.target.value)); setPage(0); }}
          rowsPerPageOptions={[10, 20, 50]}
          labelRowsPerPage="每页"
        />

        {/* Generate Report Dialog */}
        <Dialog open={generateOpen} onClose={() => !generating && setGenerateOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>生成尽调报告</DialogTitle>
          <DialogContent sx={{ pt: 1 }}>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                请选择一个已完成的任务来生成尽调报告：
              </Typography>
              <FormControl fullWidth>
                <InputLabel>选择任务</InputLabel>
                <Select
                  value={selectedTaskId}
                  label="选择任务"
                  onChange={(e) => setSelectedTaskId(e.target.value)}
                >
                  {completedTasks.map((task) => (
                    <MenuItem key={task.id} value={task.id}>
                      {task.company_name} {task.unified_social_credit_code ? `(${task.unified_social_credit_code})` : ''}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setGenerateOpen(false)} disabled={generating}>
              取消
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleGenerateReport}
              disabled={!selectedTaskId || generating}
            >
              {generating ? (
                <Stack direction="row" spacing={1} alignItems="center">
                  <CircularProgress size={20} />
                  <Typography>生成中...</Typography>
                </Stack>
              ) : (
                '生成报告'
              )}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </AppLayout>
  );
};

export default ReportListPage;
