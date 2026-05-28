import { useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { login as loginApi } from '@/api/auth';
import type { LoginRequest } from '@/types';

/** Hook for authentication state and actions */
export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  const isAuthenticated = !!token && !!user;

  const login = useCallback(
    async (req: LoginRequest) => {
      const res = await loginApi(req);
      setAuth(res.data.access_token, res.data.user);
    },
    [setAuth]
  );

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  return { user, isAuthenticated, login, logout };
}
