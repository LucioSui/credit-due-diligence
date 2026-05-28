import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Button,
  TextField,
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
  DialogContentText,
  Breadcrumbs,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  InputAdornment,
  LinearProgress,
  Alert,
  Container,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import StopIcon from '@mui/icons-material/Stop';
import HomeIcon from '@mui/icons-material/Home';
import AppLayout from '@/components/layout/AppLayout';
import { listTasks, createTask, cancelTask } from '@/api/tasks';
import type { DueDiligenceTask, CreateTaskRequest } from '@/types';
import type { ScanStatus } from '@/types';
import type { TaskFilters } from '@/types/api';

const STATUS_LABELS: Record<ScanStatus, string> = {
  pending: '待处理',
  running: '进行中',
  completed: '已完成',
  failed: '失败',
};

const STATUS_COLORS: Record<ScanStatus, 'default' | 'info' | 'success' | 'error'> = {
  pending: 'default',
  running: 'info',
  completed: 'success',
  failed: 'error',
};

const TaskListPage: React.FC = () => {
  const navigate = useNavigate();

  // Task list state
  const [tasks, setTasks] = useState<DueDiligenceTask[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Filter state
  const [statusFilter, setStatusFilter] = useState<ScanStatus | 'all'>('all');
  const [companyKeyword, setCompanyKeyword] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // Create dialog state
  const [createOpen, setCreateOpen] = useState(false);
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newUnifiedCode, setNewUnifiedCode] = useState('');
  const [creating, setCreating] = useState(false);

  // Cancel confirm dialog
  const [cancelTarget, setCancelTarget] = useState<DueDiligenceTask | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError('');
    try {
      const filters: TaskFilters = {
        page: page + 1,
        page_size: pageSize,
      };
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      if (companyKeyword.trim()) {
        filters.company_name = companyKeyword.trim();
      }
      if (startDate) {
        filters.start_date = startDate;
      }
      if (endDate) {
        filters.end_date = endDate;
      }
      const res = await listTasks(filters);
      setTasks(res.data.items);
      setTotal(res.data.total);
    } catch {
      setError('获取任务列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [page, pageSize, statusFilter, companyKeyword, startDate, endDate]);

  const handleCreate = async () => {
    if (!newCompanyName.trim()) {
      setError('请输入企业名称');
      return;
    }
    setCreating(true);
    try {
      const req: CreateTaskRequest = {
        company_name: newCompanyName.trim(),
      };
      if (newUnifiedCode.trim()) {
        req.unified_social_credit_code = newUnifiedCode.trim();
      }
      await createTask(req);
      setCreateOpen(false);
      setNewCompanyName('');
      setNewUnifiedCode('');
      setError('');
      fetchTasks();
    } catch {
      setError('创建任务失败');
    } finally {
      setCreating(false);
    }
  };

  const handleCancel = async () => {
    if (!cancelTarget) return;
    try {
      await cancelTask(cancelTarget.id);
      setCancelTarget(null);
      fetchTasks();
    } catch {
      setError('取消任务失败');
    }
  };

  return (
    <AppLayout pageTitle="尽调任务">
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
            尽调任务
          </Typography>
        </Breadcrumbs>

        {/* Title + Action */}
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
          <Typography variant="h5" fontWeight={600}>
            尽调任务
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setCreateOpen(true)}
          >
            新建任务
          </Button>
        </Stack>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Filter bar */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}>
          <FormControl sx={{ minWidth: 130 }}>
            <InputLabel size="small">状态</InputLabel>
            <Select
              value={statusFilter}
              label="状态"
              size="small"
              onChange={(e) => { setStatusFilter(e.target.value as ScanStatus | 'all'); setPage(0); }}
            >
              <MenuItem value="all">全部</MenuItem>
              <MenuItem value="pending">待处理</MenuItem>
              <MenuItem value="running">进行中</MenuItem>
              <MenuItem value="completed">已完成</MenuItem>
              <MenuItem value="failed">失败</MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="企业名称"
            value={companyKeyword}
            onChange={(e) => { setCompanyKeyword(e.target.value); setPage(0); }}
            size="small"
            sx={{ minWidth: 220 }}
            placeholder="搜索企业名称"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>
              ),
            }}
          />
          <TextField
            label="开始日期"
            type="date"
            value={startDate}
            onChange={(e) => { setStartDate(e.target.value); setPage(0); }}
            size="small"
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 160 }}
          />
          <TextField
            label="结束日期"
            type="date"
            value={endDate}
            onChange={(e) => { setEndDate(e.target.value); setPage(0); }}
            size="small"
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 160 }}
          />
        </Stack>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {/* Task Table */}
        <TableContainer component={Paper} sx={{ mb: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell width={50}>序号</TableCell>
                <TableCell>企业名称</TableCell>
                <TableCell>统一信用代码</TableCell>
                <TableCell width={100}>状态</TableCell>
                <TableCell width={100}>创建人</TableCell>
                <TableCell width={180}>创建时间</TableCell>
                <TableCell align="center" width={100}>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.length === 0 && !loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4, color: '#999' }}>
                    暂无任务数据
                  </TableCell>
                </TableRow>
              ) : (
                tasks.map((task, index) => (
                  <TableRow key={task.id} hover>
                    <TableCell>{page * pageSize + index + 1}</TableCell>
                    <TableCell>{task.company_name}</TableCell>
                    <TableCell>{task.unified_social_credit_code || '—'}</TableCell>
                    <TableCell>
                      <Chip
                        label={STATUS_LABELS[task.status]}
                        color={STATUS_COLORS[task.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{task.created_by}</TableCell>
                    <TableCell>{new Date(task.created_at).toLocaleString('zh-CN')}</TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        color="primary"
                        title="查看"
                        onClick={() => navigate(`/tasks/${task.id}`)}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                      {task.status === 'pending' || task.status === 'running' ? (
                        <IconButton
                          size="small"
                          color="error"
                          title="取消"
                          onClick={() => setCancelTarget(task)}
                        >
                          <StopIcon fontSize="small" />
                        </IconButton>
                      ) : null}
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

        {/* Create Task Dialog */}
        <Dialog open={createOpen} onClose={() => !creating && setCreateOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>新建尽调任务</DialogTitle>
          <DialogContent sx={{ pt: 1 }}>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="企业名称 *"
                value={newCompanyName}
                onChange={(e) => setNewCompanyName(e.target.value)}
                fullWidth
                required
                placeholder="请输入企业全称"
              />
              <TextField
                label="统一社会信用代码"
                value={newUnifiedCode}
                onChange={(e) => setNewUnifiedCode(e.target.value)}
                fullWidth
                placeholder="选填，18位统一社会信用代码"
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateOpen(false)} disabled={creating}>
              取消
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreate}
              disabled={creating}
            >
              {creating ? '创建中...' : '创建'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Cancel Confirm Dialog */}
        <Dialog open={Boolean(cancelTarget)} onClose={() => setCancelTarget(null)}>
          <DialogTitle>确认取消任务</DialogTitle>
          <DialogContent>
            <DialogContentText>
              确定要取消任务「{cancelTarget?.company_name}」吗？取消后将无法恢复。
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCancelTarget(null)}>取消</Button>
            <Button color="error" variant="contained" onClick={handleCancel}>
              确认取消
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </AppLayout>
  );
};

export default TaskListPage;
