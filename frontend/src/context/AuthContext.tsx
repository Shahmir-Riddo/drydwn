import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, type LoginPayload, type RegisterPayload } from '../api/auth';
import { accountsApi } from '../api/accounts';
import { getAccessToken, subscribeToTokenChanges, setAuthTokens, getRefreshToken } from '../api/client';
import type { UserProfile } from '../types';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  accessToken: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(getAccessToken());
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Subscribe to token changes
  useEffect(() => {
    return subscribeToTokenChanges((newToken) => {
      setToken(newToken);
    });
  }, []);

  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      return;
    }
    try {
      const profile = await accountsApi.getMyProfile();
      setUser(profile);
    } catch {
      setUser(null);
    }
  }, []);

  // Initial session bootstrap: try refresh token if present
  useEffect(() => {
    const bootstrap = async () => {
      const refresh = getRefreshToken();
      if (refresh) {
        try {
          const newToken = await authApi.refreshToken();
          if (newToken) {
            const profile = await accountsApi.getMyProfile();
            setUser(profile);
          }
        } catch {
          setAuthTokens(null, null);
        }
      }
      setIsLoading(false);
    };

    bootstrap();
  }, []);

  const login = async (payload: LoginPayload) => {
    await authApi.login(payload);
    const profile = await accountsApi.getMyProfile();
    setUser(profile);
  };

  const register = async (payload: RegisterPayload) => {
    await authApi.register(payload);
    const profile = await accountsApi.getMyProfile();
    setUser(profile);
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!token,
        isLoading,
        accessToken: token,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
