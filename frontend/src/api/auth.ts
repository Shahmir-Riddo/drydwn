import { apiClient, setAuthTokens, getRefreshToken } from './client';
import axios from 'axios';

export interface LoginPayload {
  username?: string;
  email?: string;
  password?: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<AuthTokens> => {
    const res = await apiClient.post<AuthTokens>('/auth/token/', payload);
    setAuthTokens(res.data.access, res.data.refresh);
    return res.data;
  },

  register: async (payload: RegisterPayload): Promise<AuthTokens & { detail?: string; username?: string }> => {
    const res = await apiClient.post<AuthTokens & { detail?: string; username?: string }>('/auth/register/', payload);
    if (res.data.access && res.data.refresh) {
      setAuthTokens(res.data.access, res.data.refresh);
    }
    return res.data;
  },

  refreshToken: async (): Promise<string | null> => {
    const refresh = getRefreshToken();
    if (!refresh) return null;
    try {
      const res = await axios.post<{ access: string; refresh?: string }>('/api/v1/auth/token/refresh/', {
        refresh,
      });
      setAuthTokens(res.data.access, res.data.refresh || refresh);
      return res.data.access;
    } catch {
      setAuthTokens(null, null);
      return null;
    }
  },

  logout: () => {
    setAuthTokens(null, null);
  },
};
