import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Avatar,
  Box,
  IconButton,
  Chip,
  Menu,
  MenuItem,
} from '@mui/material';
import { ExitToApp as ExitToAppIcon } from '@mui/icons-material';
import { useAuth } from '@/hooks/useAuth';

interface TopBarProps {
  pageTitle?: string;
}

const roleLabels: Record<string, string> = {
  admin: '管理员',
  approver: '审批员',
  supervisor: '主管',
  viewer: '查看者',
};

const TopBar: React.FC<TopBarProps> = ({ pageTitle }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const { user, logout } = useAuth();

  const userName = user?.real_name || user?.username || '用户';
  const userRole = user?.role || 'viewer';
  const userAvatar = userName.charAt(0);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
  };

  return (
    <AppBar
      position="sticky"
      elevation={1}
      sx={{
        bgcolor: '#fff',
        color: '#333',
        borderBottom: '1px solid #e0e0e0',
      }}
    >
      <Toolbar variant="dense">
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem', mr: 3 }}>
          {pageTitle || '仪表盘'}
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            label={roleLabels[userRole] || userRole}
            size="small"
            sx={{ bgcolor: '#e3f2fd', color: '#1565C0', fontWeight: 500 }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer' }} onClick={handleMenuOpen}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: '#1565C0', fontSize: '0.8rem' }}>
              {userAvatar}
            </Avatar>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              {userName}
            </Typography>
          </Box>
          <IconButton color="inherit" onClick={handleLogout} title="退出登录">
            <ExitToAppIcon />
          </IconButton>
        </Box>
      </Toolbar>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleLogout}>退出登录</MenuItem>
      </Menu>
    </AppBar>
  );
};

export default TopBar;
