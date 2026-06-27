import type {
  EmailVerification,
  LoginRequest,
  PasswordReset,
  PasswordResetConfirm,
  RegisterRequest,
  TokenResponse,
  User,
  UserUpdate,
} from '@/types/auth.types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000';

async function request<T>(
  path: string,
  init?: RequestInit,
  token?: string | null
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    const message =
      error?.detail || error?.error?.message || `Auth request failed: ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

const AuthAPI = {
  login(data: LoginRequest) {
    return request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  register(data: RegisterRequest) {
    return request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  me(token: string) {
    return request<User>('/auth/me', undefined, token);
  },

  updateProfile(data: UserUpdate, token: string) {
    return request<User>(
      '/users/profile',
      {
        method: 'PUT',
        body: JSON.stringify(data),
      },
      token
    );
  },

  logout(token?: string | null) {
    return request<{ message: string }>(
      '/auth/logout',
      { method: 'POST' },
      token
    );
  },

  requestPasswordReset(data: PasswordReset) {
    return request<{ message: string }>('/auth/request-password-reset', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  resetPassword(data: PasswordResetConfirm) {
    return request<{ message: string; reset: boolean }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  verifyEmail(data: EmailVerification) {
    return request<{ message: string; verified: boolean }>('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

export default AuthAPI;
