import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios';

// In-memory token store (avoids XSS vulnerabilities associated with localStorage)
let accessToken: string | null = null;
let refreshToken: string | null = null;

// Callbacks for notifying listeners when token state changes
type TokenListener = (token: string | null) => void;
const listeners: Set<TokenListener> = new Set();

export const setAuthTokens = (access: string | null, refresh?: string | null) => {
  accessToken = access;
  if (refresh !== undefined) {
    refreshToken = refresh;
    if (refresh) {
      sessionStorage.setItem('drydown_refresh_token', refresh);
    } else {
      sessionStorage.removeItem('drydown_refresh_token');
    }
  }
  listeners.forEach((listener) => listener(accessToken));
};

export const getAccessToken = () => accessToken;
export const getRefreshToken = () => {
  if (!refreshToken) {
    refreshToken = sessionStorage.getItem('drydown_refresh_token');
  }
  return refreshToken;
};

export const subscribeToTokenChanges = (listener: TokenListener) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach in-memory JWT token if available
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 and refresh token with queueing
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
  config: AxiosRequestConfig;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      if (token && prom.config.headers) {
        prom.config.headers['Authorization'] = `Bearer ${token}`;
      }
      prom.resolve(apiClient(prom.config));
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Do not attempt refresh on login or refresh endpoint failures
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/token/')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalRequest });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedRefresh = getRefreshToken();
      if (!storedRefresh) {
        setAuthTokens(null, null);
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const response = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: storedRefresh,
        });

        const newAccess = response.data.access;
        const newRefresh = response.data.refresh || storedRefresh;
        setAuthTokens(newAccess, newRefresh);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        }
        processQueue(null, newAccess);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        setAuthTokens(null, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
