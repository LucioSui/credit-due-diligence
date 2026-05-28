import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  LinearProgress,
  Stack,
  Alert,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { login as apiLogin } from '@/api/auth';
import { useAuthStore } from '@/stores/authStore';
import type { User } from '@/types';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('请输入用户名和密码');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await apiLogin({ username, password });
      setAuth(res.data.access_token, res.data.user);
      navigate('/');
    } catch {
      // Demo mode: auto-login with mock admin user
      const mockUser: User = {
        id: 'demo',
        username: username,
        email: `${username}@demo.com`,
        role: 'admin',
        is_active: true,
        created_at: new Date().toISOString(),
      };
      setAuth('demo-token', mockUser);
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        bgcolor: '#f5f5f5',
      }}
    >
      {loading && <LinearProgress sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }} />}
      <Card sx={{ maxWidth: 400, width: '100%', px: 2 }}>
        <CardContent sx={{ pt: 5, pb: 3, px: 4 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                bgcolor: 'primary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 1.5,
              }}
            >
              <LockOutlinedIcon sx={{ fontSize: 28, color: 'primary.contrastText' }} />
            </Box>
            <Typography variant="h5" color="primary" fontWeight={600} textAlign="center">
              银行授信尽调系统
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              请登录您的账号
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                label="用户名"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                fullWidth
                autoComplete="username"
                required
              />
              <TextField
                label="密码"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                autoComplete="current-password"
                required
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 1 }}
              >
                登录
              </Button>
            </Stack>
          </form>

          <Typography variant="caption" color="text.secondary" align="center" sx={{ display: 'block', mt: 2 }}>
            演示模式：输入任意账号密码即可登录
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;
