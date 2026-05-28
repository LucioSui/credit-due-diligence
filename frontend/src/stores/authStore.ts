import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  setUser: (user: User) => void;
  clearAuth: () => void;
  isAuthenticated: boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setAuth: (token: string, user: User) => set({ token, user }),
      setUser: (user: User) => set({ user }),
      clearAuth: () => set({ token: null, user: null }),
      get isAuthenticated() {
        return !!get().token && !!get().user;
      },
    }),
    { name: 'auth-storage' }
  )
);
