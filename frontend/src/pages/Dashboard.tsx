import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
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
  Alert,
  LinearProgress,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CancelIcon from '@mui/icons-material/CancelPresentation';
import { listTasks, createTask, cancelTask } from '@/api/tasks';
import CompanySearch from '@/components/common/CompanySearch';
import RatingBadge from '@/components/common/RatingBadge';
import type { DueDiligenceTask, ScanStatus } from '@/types';

const STATUS_MAP: Record<ScanStatus, string> = {
  pending: '待扫描',
  running: '扫描中',
  completed: '已完成',
  failed: '失败',
};

const STATUS_COLOR: Record<ScanStatus, 'default' | 'info' | 'success' | 'error'> = {
  pending: 'default',
  running: 'info',
  completed: 'success',
  failed: 'error',
};

/** Calculate overall progress from scan_progress */
function calcProgress(task: DueDiligenceTask): number {
  if (!task.scan_progress) return task.status === 'completed' ? 100 : 0;
  const steps = Object.values(task.scan_progress);
  const total = steps.length;
  if (total === 0) return 0;
  const done = steps.filter((s) => s === 'completed').length;
  return Math.round((done / total) * 100);
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<DueDiligenceTask[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState<ScanStatus | ''>('');
  const [keyword, setKeyword] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [createOpen, setCreateOpen] = useState(false);
  const [cancelTarget, setCancelTarget] = useState<DueDiligenceTask | null>(null);
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newUnifiedCode, setNewUnifiedCode] = useState('');
  const [newRemark, setNewRemark] = useState('');

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const res = await listTasks({
        status: (statusFilter as ScanStatus) || undefined,
        page: page + 1,
        page_size: pageSize,
      });
      setTasks(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch {
      setError('获取任务列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [statusFilter, page, pageSize]);

  const filtered = tasks.filter((t) => {
    const kw = keyword.toLowerCase();
    if (!kw) return true;
    return t.id.toLowerCase().includes(kw) || t.company_name.toLowerCase().includes(kw);
  });

  const handleCreate = async () => {
    if (!newCompanyName) {
      setError('请选择或输入企业名称');
      return;
    }
    try {
      await createTask({
        company_name: newCompanyName,
        unified_social_credit_code: newUnifiedCode || undefined,
        remark: newRemark || undefined,
      });
      setCreateOpen(false);
      setNewCompanyName('');
      setNewUnifiedCode('');
      setNewRemark('');
      setError('');
      fetchTasks();
    } catch {
      setError('创建任务失败');
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

  const handleCompanySelect = (name: string) => {
    setNewCompanyName(name);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          工作台
        </Typography>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)}>
          新建任务
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filter bar */}
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel size="small">状态</InputLabel>
          <Select
            value={statusFilter}
            label="状态"
            size="small"
            onChange={(e) => { setStatusFilter(e.target.value as ScanStatus | ''); setPage(0); }}
          >
            <MenuItem value="">全部</MenuItem>
            <MenuItem value="pending">待扫描</MenuItem>
            <MenuItem value="running">扫描中</MenuItem>
            <MenuItem value="completed">已完成</MenuItem>
            <MenuItem value="failed">失败</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="关键词搜索"
          value={keyword}
          onChange={(e) => { setKeyword(e.target.value); setPage(0); }}
          size="small"
          sx={{ minWidth: 220 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>
            ),
          }}
        />
        <FormControl sx={{ minWidth: 100 }}>
          <InputLabel size="small">每页</InputLabel>
          <Select
            value={pageSize}
            label="每页"
            size="small"
            onChange={(e) => { setPageSize(Number(e.target.value)); setPage(0); }}
          >
            <MenuItem value={10}>10</MenuItem>
            <MenuItem value={20}>20</MenuItem>
            <MenuItem value={50}>50</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {loading ? (
        <LinearProgress sx={{ mb: 2 }} />
      ) : (
        <>
          <TableContainer component={Paper} sx={{ mb: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>任务ID</TableCell>
                  <TableCell>企业名称</TableCell>
                  <TableCell>状态</TableCell>
                  <TableCell>评级</TableCell>
                  <TableCell>进度</TableCell>
                  <TableCell>创建时间</TableCell>
                  <TableCell align="center">操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: '#999' }}>
                      暂无数据
                    </TableCell>
                  </TableRow>
                ) : (
                  filtered.map((task) => (
                    <TableRow
                      key={task.id}
                      hover
                      onClick={() => navigate(`/task/${task.id}`)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>{task.id.slice(0, 8)}</TableCell>
                      <TableCell>{task.company_name}</TableCell>
                      <TableCell>
                        <Chip label={STATUS_MAP[task.status]} color={STATUS_COLOR[task.status] as any} size="small" />
                      </TableCell>
                      <TableCell>
                        {task.rating_result ? (
                          <RatingBadge grade={task.rating_result.grade} size="small" />
                        ) : (
                          '—'
                        )}
                      </TableCell>
                      <TableCell sx={{ width: 200 }}>
                        <LinearProgress variant="determinate" value={calcProgress(task)} sx={{ minWidth: 100 }} />
                        <Typography variant="caption" color="text.secondary">{calcProgress(task)}%</Typography>
                      </TableCell>
                      <TableCell>{new Date(task.created_at).toLocaleString('zh-CN')}</TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => { e.stopPropagation(); navigate(`/task/${task.id}`); }}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => { e.stopPropagation(); setCancelTarget(task); }}
                        >
                          <CancelIcon fontSize="small" />
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
          />
        </>
      )}

      {/* Create Dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>新建尽调任务</DialogTitle>
        <DialogContent sx={{ pt: 1 }}>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <CompanySearch onSelect={handleCompanySelect} value={newCompanyName} />
            <TextField
              label="统一社会信用代码（可选）"
              value={newUnifiedCode}
              onChange={(e) => setNewUnifiedCode(e.target.value)}
              fullWidth
            />
            <TextField
              label="备注"
              multiline
              rows={2}
              value={newRemark}
              onChange={(e) => setNewRemark(e.target.value)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>取消</Button>
          <Button variant="contained" color="primary" onClick={handleCreate}>
            创建
          </Button>
        </DialogActions>
      </Dialog>

      {/* Cancel Confirm Dialog */}
      <Dialog open={Boolean(cancelTarget)} onClose={() => setCancelTarget(null)}>
        <DialogTitle>确认取消</DialogTitle>
        <DialogContent>
          <DialogContentText>
            确定要取消任务「{cancelTarget?.id.slice(0, 8)} — {cancelTarget?.company_name}」吗？
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelTarget(null)}>取消</Button>
          <Button color="error" variant="contained" onClick={handleCancel}>
            确认取消
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;
