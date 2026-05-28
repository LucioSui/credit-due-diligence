import React from 'react';
import { Navigate } from 'react-router-dom';
import { Alert } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';
import type { User } from '@/types/index';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: User['role'][];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Alert severity="error" variant="filled" sx={{ maxWidth: 400 }}>
          无权限访问此页面
        </Alert>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
