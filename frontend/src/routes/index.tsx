import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from './ProtectedRoute';

/* Code-splitting: lazy-load each page so the initial bundle stays small.
 * Each `React.lazy()` call creates a separate chunk that Vite extracts on build. */
const Login = React.lazy(() => import('@/pages/Login'));
const Dashboard = React.lazy(() => import('@/pages/Dashboard'));
const TaskDetail = React.lazy(() => import('@/pages/TaskDetail'));
const ReportPreview = React.lazy(() => import('@/pages/ReportPreview'));
const TaskListPage = React.lazy(() => import('@/pages/TaskListPage'));
const RatingPage = React.lazy(() => import('@/pages/RatingPage'));
const ReportListPage = React.lazy(() => import('@/pages/ReportListPage'));
const UserManagement = React.lazy(() => import('@/pages/UserManagement'));

/* Lightweight fallback shown while a lazy chunk is being downloaded. */
const PageLoadingFallback: React.FC = () => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
    fontSize: '1rem',
    color: '#999',
  }}>
    页面加载中...
  </div>
);

const Router: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login — no layout, no auth */}
        <Route path="/login" element={
          <Suspense fallback={<PageLoadingFallback />}>
            <Login />
          </Suspense>
        } />

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
                <Suspense fallback={<PageLoadingFallback />}>
                  <Dashboard />
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/task/:taskId"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Suspense fallback={<PageLoadingFallback />}>
                  <TaskDetail />
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/report/:reportId"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Suspense fallback={<PageLoadingFallback />}>
                  <ReportPreview />
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Suspense fallback={<PageLoadingFallback />}>
                  <TaskListPage />
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/rating"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Suspense fallback={<PageLoadingFallback />}>
                  <RatingPage />
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Suspense fallback={<PageLoadingFallback />}>
                  <ReportListPage />
                </Suspense>
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AppLayout>
                <Suspense fallback={<PageLoadingFallback />}>
                  <UserManagement />
                </Suspense>
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
