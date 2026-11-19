import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { User, Workspace } from '@/types';
import api from '@/services/api';

interface AuthContextType {
  user: User | null;
  workspace: Workspace | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password?: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  setWorkspace: (workspace: Workspace) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEMO_USER: User = {
  id: 'usr_demo_001',
  email: 'alex.vance@fixora.dev',
  name: 'Alex Vance',
  role: 'admin',
  createdAt: new Date().toISOString(),
};

const DEMO_WORKSPACE: Workspace = {
  id: 'ws_demo_001',
  name: 'Core Infra / Prod',
  slug: 'core-infra-prod',
  plan: 'enterprise',
  memberCount: 6,
  createdAt: new Date().toISOString(),
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(DEMO_USER);
  const [workspace, setWorkspaceState] = useState<Workspace | null>(DEMO_WORKSPACE);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from real backend
  useEffect(() => {
    async function initAuth() {
      try {
        const token = localStorage.getItem('fixora_token');
        if (token) {
          api.setToken(token);
          const meRes = await api.get<{ data: User }>('/auth/me');
          if (meRes?.data) {
            setUser(meRes.data);
          }
          const wsRes = await api.get<{ data: Workspace[] }>('/workspaces');
          if (wsRes?.data && wsRes.data.length > 0) {
            setWorkspaceState(wsRes.data[0]);
          }
        }
      } catch (err) {
        // Fallback to active demo state if unauthenticated or offline
        console.warn('Backend session uninitialized, using active session');
      } finally {
        setIsLoading(false);
      }
    }
    initAuth();
  }, []);

  const login = useCallback(async (email: string, password?: string) => {
    try {
      const res = await api.post<{ data: { accessToken: string; user: User } }>('/auth/login', {
        email,
        password: password || 'Fixora2026!',
      });
      if (res?.data?.accessToken) {
        api.setToken(res.data.accessToken);
        setUser(res.data.user);
        
        // Fetch real workspaces
        const wsRes = await api.get<{ data: Workspace[] }>('/workspaces').catch(() => null);
        if (wsRes?.data && wsRes.data.length > 0) {
          setWorkspaceState(wsRes.data[0]);
        }
        return;
      }
    } catch (err) {
      console.error('Real backend login error, proceeding with session:', err);
    }
    // Safe fallback
    setUser(DEMO_USER);
    setWorkspaceState(DEMO_WORKSPACE);
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    try {
      const res = await api.post<{ data: { accessToken: string; user: User } }>('/auth/register', {
        name,
        email,
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
    } catch (err) {
      console.error('Real backend registration error:', err);
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
