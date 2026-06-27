import { create } from 'zustand';
import AuthAPI from '@/lib/api/auth';
import type {
  AuthState,
  LoginRequest,
  RegisterRequest,
  UserUpdate,
} from '@/types/auth.types';

interface AuthStore extends AuthState {
  initialize: () => Promise<void>;
  login: (data: LoginRequest) => Promise<boolean>;
  register: (data: RegisterRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  updateProfile: (data: UserUpdate) => Promise<boolean>;
  setError: (error: string | null) => void;
}

const tokenKey = 'access_token';

function getStoredToken() {
  if (typeof window === 'undefined') {
    return null;
  }
  return localStorage.getItem(tokenKey);
}

function setStoredToken(token: string | null) {
  if (typeof window === 'undefined') {
    return;
  }

  if (token) {
    localStorage.setItem(tokenKey, token);
  } else {
    localStorage.removeItem(tokenKey);
  }
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  setError: (error) => set({ error }),

  initialize: async () => {
    const token = getStoredToken();
    if (!token) {
      set({ isLoading: false, user: null, token: null, isAuthenticated: false });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const user = await AuthAPI.me(token);
      set({ user, token, isAuthenticated: true, isLoading: false });
    } catch (error) {
      setStoredToken(null);
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : '认证状态已失效',
      });
    }
  },

  login: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const result = await AuthAPI.login(data);
      setStoredToken(result.access_token);
      set({
        user: result.user,
        token: result.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
      return true;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '登录失败',
      });
      return false;
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await AuthAPI.register(data);
      set({ isLoading: false });
      return true;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '注册失败',
      });
      return false;
    }
  },

  logout: async () => {
    const token = get().token || getStoredToken();
    try {
      await AuthAPI.logout(token);
    } catch {
      // Local logout must still clear stale credentials if the API is unavailable.
    } finally {
      setStoredToken(null);
      set({ user: null, token: null, isAuthenticated: false, error: null });
    }
  },

  updateProfile: async (data) => {
    const token = get().token || getStoredToken();
    if (!token) {
      set({ error: '请先登录' });
      return false;
    }

    set({ isLoading: true, error: null });
    try {
      const user = await AuthAPI.updateProfile(data, token);
      set({ user, isLoading: false });
      return true;
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '资料更新失败',
      });
      return false;
    }
  },
}));
