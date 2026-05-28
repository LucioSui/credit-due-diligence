import axios from 'axios';
import type { ApiResponse } from '@/types/api';
import { useAuthStore } from '@/stores/authStore';

const api = axios.create({ baseURL: '/api', timeout: 30000 });

// Request interceptor: attach token from authStore
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
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
