import React, { useCallback, useMemo, useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import {
  listUsers,
  createUser,
  updateUser,
  deleteUser,
  type UserCreateRequest,
  type UserUpdateRequest,
} from '@/api/user';
import type { User } from '@/types';

const ROLE_OPTIONS: { value: User['role']; label: string; color: string }[] = [
  { value: 'admin', label: '管理员', color: '#d32f2f' },
  { value: 'approver', label: '审批员', color: '#f57c00' },
  { value: 'supervisor', label: '主管', color: '#1976d2' },
  { value: 'viewer', label: '查看者', color: '#388e3c' },
];

function roleColor(role: string): string {
  return ROLE_OPTIONS.find((r) => r.value === role)?.color || '#757575';
}

export default function UserManagement() {
  const theme = useTheme();

  // --- State ---
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(false);
  const [searchKey, setSearchKey] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog state
  const [openForm, setOpenForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [openDelete, setOpenDelete] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);

  // Form state
  const [formUsername, setFormUsername] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formPassword, setFormPassword] = useState('');
  const [formRole, setFormRole] = useState<User['role']>('viewer');
  const [formRealName, setFormRealName] = useState('');
  const [formIsActive, setFormIsActive] = useState(true);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // --- Data fetching ---
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listUsers(page + 1, pageSize);
      setUsers(res.data.items);
      setTotal(res.data.total);
    } catch (err: any) {
      setError(err.response?.data?.message || '获取用户列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize]);

  React.useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Filtered users (client-side search)
  const filteredUsers = useMemo(() => {
    if (!searchKey.trim()) return users;
    const kw = searchKey.toLowerCase();
    return users.filter(
      (u) =>
        u.username.toLowerCase().includes(kw) ||
        u.email.toLowerCase().includes(kw) ||
        (u.real_name && u.real_name.toLowerCase().includes(kw))
    );
  }, [users, searchKey]);

  // --- Form helpers ---
  const resetForm = () => {
    setEditingUser(null);
    setFormUsername('');
    setFormEmail('');
    setFormPassword('');
    setFormRole('viewer');
    setFormRealName('');
    setFormIsActive(true);
    setFormErrors({});
  };

  const openCreate = () => {
    resetForm();
    setOpenForm(true);
  };

  const openEdit = (user: User) => {
    resetForm();
    setEditingUser(user);
    setFormUsername(user.username);
    setFormEmail(user.email);
    setFormRole(user.role);
    setFormRealName(user.real_name || '');
    setFormIsActive(user.is_active);
    setOpenForm(true);
  };

  const validateForm = (): boolean => {
    const errs: Record<string, string> = {};
    if (!formUsername.trim()) errs.username = '请输入用户名';
    else if (formUsername.length < 3) errs.username = '用户名至少3个字符';
    if (!formEmail.trim()) errs.email = '请输入邮箱';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formEmail)) errs.email = '邮箱格式不正确';
    if (!editingUser && !formPassword) errs.password = '请输入密码';
    if (editingUser && formPassword && formPassword.length < 6) errs.password = '密码至少6个字符';
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;
    setError(null);
    setSuccess(null);
    try {
      if (editingUser) {
        const payload: UserUpdateRequest = {
          email: formEmail,
          role: formRole,
          real_name: formRealName || undefined,
          is_active: formIsActive,
        };
        if (formPassword) payload.password = formPassword;
        await updateUser(editingUser.id, payload);
        // Refresh current user if self-editing
        setSuccess('用户更新成功');
      } else {
        const payload: UserCreateRequest = {
          username: formUsername,
          email: formEmail,
          password: formPassword,
          role: formRole,
          real_name: formRealName || undefined,
        };
        await createUser(payload);
        setSuccess('用户创建成功');
      }
      setOpenForm(false);
      resetForm();
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.message || '操作失败');
    }
  };

  // --- Delete ---
  const openDeleteDialog = (user: User) => {
    setDeleteTarget(user);
    setOpenDelete(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setError(null);
    setSuccess(null);
    try {
      await deleteUser(deleteTarget.id);
      setSuccess('用户已禁用');
      setOpenDelete(false);
      setDeleteTarget(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.message || '删除失败');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            用户管理
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            管理系统用户账号、角色分配与权限控制
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={openCreate}
          sx={{ bgcolor: '#1565C0', '&:hover': { bgcolor: '#0d47a1' } }}
        >
          新增用户
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Toolbar */}
      <Paper sx={{ p: 1.5, mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <TextField
          size="small"
          placeholder="搜索用户名 / 邮箱 / 姓名"
          value={searchKey}
          onChange={(e) => setSearchKey(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          sx={{ flex: 1, maxWidth: 400 }}
        />
        <IconButton onClick={fetchUsers} title="刷新">
          <RefreshIcon />
        </IconButton>
        <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
          共 {searchKey ? filteredUsers.length : total} 条记录
        </Typography>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper} sx={{ boxShadow: 'none', border: `1px solid ${theme.palette.divider}` }}>
        <Table size="small">
          <TableHead>
            <TableRow
              sx={{
                bgcolor: alpha('#1565C0', 0.04),
                '& th': { fontWeight: 600, fontSize: '0.8rem', color: '#555' },
              }}
            >
              <TableCell>用户名</TableCell>
              <TableCell>邮箱</TableCell>
              <TableCell>姓名</TableCell>
              <TableCell>角色</TableCell>
              <TableCell>状态</TableCell>
              <TableCell>创建时间</TableCell>
              <TableCell align="right">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : filteredUsers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 6, color: '#999' }}>
                  {searchKey ? '未找到匹配的用户' : '暂无用户数据'}
                </TableCell>
              </TableRow>
            ) : (
              filteredUsers.map((user) => (
                <TableRow key={user.id} hover sx={{ '&:not(:last-child) td': { borderBottom: `1px solid ${theme.palette.divider}` } }}>
                  <TableCell sx={{ fontWeight: 500 }}>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.real_name || '—'}</TableCell>
                  <TableCell>
                    <Chip
                      label={ROLE_OPTIONS.find((r) => r.value === user.role)?.label || user.role}
                      size="small"
                      sx={{
                        bgcolor: alpha(roleColor(user.role), 0.12),
                        color: roleColor(user.role),
                        fontWeight: 500,
                        fontSize: '0.72rem',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.is_active ? '正常' : '已禁用'}
                      size="small"
                      color={user.is_active ? 'success' : 'default'}
                      variant="outlined"
                      sx={{ fontSize: '0.72rem' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString('zh-CN') : '—'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="编辑">
                      <IconButton size="small" onClick={() => openEdit(user)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={user.is_active ? '禁用' : '启用'}>
                      <IconButton size="small" onClick={() => openDeleteDialog(user)}>
                        <DeleteIcon fontSize="small" color={user.is_active ? 'action' : 'disabled'} />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {!loading && filteredUsers.length > 0 && (
        <TablePagination
          component="div"
          count={searchKey ? filteredUsers.length : total}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={pageSize}
          onRowsPerPageChange={(e) => {
            setPageSize(Number(e.target.value));
            setPage(0);
          }}
          rowsPerPageOptions={[10, 20, 50, 100]}
          labelRowsPerPage="每页条数"
        />
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openForm} onClose={() => setOpenForm(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingUser ? '编辑用户' : '新增用户'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Username — read-only in edit mode */}
          <TextField
            label="用户名"
            fullWidth
            value={formUsername}
            onChange={(e) => setFormUsername(e.target.value)}
            error={!!formErrors.username}
            helperText={formErrors.username}
            inputProps={{ readOnly: !!editingUser }}
          />
          <TextField
            label="邮箱"
            fullWidth
            type="email"
            value={formEmail}
            onChange={(e) => setFormEmail(e.target.value)}
            error={!!formErrors.email}
            helperText={formErrors.email}
          />
          <TextField
            label={editingUser ? '新密码（留空则不修改）' : '密码'}
            fullWidth
            type="password"
            value={formPassword}
            onChange={(e) => setFormPassword(e.target.value)}
            error={!!formErrors.password}
            helperText={formErrors.password}
          />
          <FormControl fullWidth error={!!formErrors.role}>
            <InputLabel>角色</InputLabel>
            <Select value={formRole} label="角色" onChange={(e) => setFormRole(e.target.value as User['role'])}>
              {ROLE_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="姓名（可选）"
            fullWidth
            value={formRealName}
            onChange={(e) => setFormRealName(e.target.value)}
          />
          {editingUser && (
            <FormControlLabel
              control={
                <Switch checked={formIsActive} onChange={(_, v) => setFormIsActive(v)} />
              }
              label={formIsActive ? '账号正常' : '账号禁用'}
            />
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenForm(false)}>取消</Button>
          <Button variant="contained" onClick={handleSave} sx={{ bgcolor: '#1565C0' }}>
            {editingUser ? '保存' : '创建'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={openDelete} onClose={() => setOpenDelete(false)} maxWidth="xs" fullWidth>
        <DialogTitle>确认操作</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Typography>
            确定要{deleteTarget?.is_active ? '禁用' : '启用'}用户「<strong>{deleteTarget?.username}</strong>」吗？
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 1, fontSize: '0.85rem' }}>
            {deleteTarget?.is_active
              ? '禁用后该用户将无法登录系统。'
              : '启用后该用户将恢复登录权限。'}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenDelete(false)}>取消</Button>
          <Button
            variant="contained"
            color={deleteTarget?.is_active ? 'error' : 'primary'}
            onClick={handleDelete}
          >
            {deleteTarget?.is_active ? '禁用' : '启用'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
