import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { User, Workspace } from '@/types';
import api from '@/services/api';

interface AuthContextType {
  user: User | null;
  workspace: Workspace | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  setWorkspace: (workspace: Workspace) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspaceState] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from verified backend token
  useEffect(() => {
    async function initAuth() {
      try {
        const token = localStorage.getItem('fixora_token');
        if (token) {
          api.setToken(token);
          const meRes = await api.get<{ data: User }>('/auth/me');
          if (meRes?.data) {
            setUser(meRes.data);
            const wsRes = await api.get<{ data: Workspace[] }>('/workspaces').catch(() => null);
            if (wsRes?.data && wsRes.data.length > 0) {
              setWorkspaceState(wsRes.data[0]);
            }
          } else {
            api.clearToken();
            setUser(null);
            setWorkspaceState(null);
          }
        } else {
          setUser(null);
          setWorkspaceState(null);
        }
      } catch (err) {
        console.warn('Session verification failed, remaining unauthenticated:', err);
        api.clearToken();
        setUser(null);
        setWorkspaceState(null);
      } finally {
        setIsLoading(false);
      }
    }
    initAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const res = await api.post<{ data: { accessToken: string; user: User } }>('/auth/login', {
        email: email.trim(),
        password,
      });
      if (res?.data?.accessToken) {
        api.setToken(res.data.accessToken);
        setUser(res.data.user);

        // Fetch real workspaces for the authenticated user
        const wsRes = await api.get<{ data: Workspace[] }>('/workspaces').catch(() => null);
        if (wsRes?.data && wsRes.data.length > 0) {
          setWorkspaceState(wsRes.data[0]);
        }
        return;
      }
      throw new Error('Authentication failed: no access token returned.');
    } catch (err) {
      console.error('Authentication error:', err);
      api.clearToken();
      setUser(null);
      setWorkspaceState(null);
      throw err;
    }
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    try {
      const res = await api.post<{ data: { accessToken: string; user: User } }>('/auth/register', {
        name: name.trim(),
        email: email.trim(),
        password,
      });
      if (res?.data?.accessToken) {
        api.setToken(res.data.accessToken);
        setUser(res.data.user);
        const wsRes = await api.get<{ data: Workspace[] }>('/workspaces').catch(() => null);
        if (wsRes?.data && wsRes.data.length > 0) {
          setWorkspaceState(wsRes.data[0]);
        }
        return;
      }
      throw new Error('Registration failed: no access token returned.');
    } catch (err) {
      console.error('Registration error:', err);
      api.clearToken();
      setUser(null);
      setWorkspaceState(null);
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    api.clearToken();
    setUser(null);
    setWorkspaceState(null);
  }, []);

  const setWorkspace = useCallback((ws: Workspace) => {
    setWorkspaceState(ws);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        workspace,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        setWorkspace,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
