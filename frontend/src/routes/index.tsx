import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from './ProtectedRoute';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import TaskDetail from '@/pages/TaskDetail';
import ReportPreview from '@/pages/ReportPreview';
import TaskListPage from '@/pages/TaskListPage';
import RatingPage from '@/pages/RatingPage';
import ReportListPage from '@/pages/ReportListPage';
import UserManagement from '@/pages/UserManagement';

const Router: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login — no layout, no auth */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes — wrapped in AppLayout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Navigate to="/dashboard" replace />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Dashboard />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/task/:taskId"
          element={
            <ProtectedRoute>
              <AppLayout>
                <TaskDetail />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/report/:reportId"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ReportPreview />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <AppLayout>
                <TaskListPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/rating"
          element={
            <ProtectedRoute>
              <AppLayout>
                <RatingPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ReportListPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AppLayout>
                <UserManagement />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        {/* 404 */}
        <Route
          path="*"
          element={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', fontSize: '1.2rem', color: '#999' }}>
              404 — 页面不存在
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
