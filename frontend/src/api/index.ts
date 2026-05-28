import axios from 'axios';
import type { ApiResponse } from '@/types/api';
import { useAuthStore } from '@/stores/authStore';

const api = axios.create({ baseURL: '/api', timeout: 30000 });
const AUTH_STORAGE_KEY = 'auth-storage';

/**
 * Read token from both Zustand store and localStorage.
 * Zustand persist hydration is async — on page refresh, the store may
 * not be hydrated yet when the first API call fires. Reading directly
 * from localStorage ensures we always have the latest persisted token.
 */
function getToken(): string | null {
  // 1. Try Zustand store (already hydrated)
  const token = useAuthStore.getState().token;
  if (token) return token;

  // 2. Fallback: read directly from localStorage
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed?.state?.token) return parsed.state.token;
    }
  } catch {
    // ignore parse errors
  }
  return null;
}

// Request interceptor: attach token from authStore or localStorage
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor: unwrap data, handle errors
api.interceptors.response.use(
  (response) => {
    const res: ApiResponse = response.data;
    if (res.code === 0) return res as any;
    return Promise.reject(new Error((res as any).message || '请求失败'));
  },
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
