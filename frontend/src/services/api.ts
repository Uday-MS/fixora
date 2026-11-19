const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export class ApiError extends Error {
  statusCode: number;
  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.name = 'ApiError';
  }
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.token = typeof window !== 'undefined' ? localStorage.getItem('fixora_token') : null;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('fixora_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('fixora_token');
  }

  private async request<T>(endpoint: string, options: RequestInit & { params?: Record<string, string> } = {}): Promise<T> {
    const { params, ...init } = options;
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(init.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, { ...init, headers });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ message: response.statusText || 'Request failed' }));
        throw new ApiError(errData.message || 'Request failed', response.status);
      }
      if (response.status === 204) return {} as T;
      return await response.json();
    } catch (err: any) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(err.message || 'Network error connecting to Fixora backend', 503);
    }
  }

  get<T>(endpoint: string, params?: Record<string, string>) {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  post<T>(endpoint: string, data?: unknown) {
    return this.request<T>(endpoint, { method: 'POST', body: data ? JSON.stringify(data) : undefined });
  }

  patch<T>(endpoint: string, data?: unknown) {
    return this.request<T>(endpoint, { method: 'PATCH', body: data ? JSON.stringify(data) : undefined });
  }

  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  upload<T>(endpoint: string, file: File, fieldName = 'file', extraFields?: Record<string, string>) {
    const formData = new FormData();
    formData.append(fieldName, file);
    if (extraFields) {
      for (const [k, v] of Object.entries(extraFields)) {
        if (v) formData.append(k, v);
      }
    }
    const headers: Record<string, string> = {};
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    return fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      body: formData,
      headers,
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
        throw new ApiError(err.detail || err.message || 'Upload failed', res.status);
      }
      return res.json() as Promise<T>;
    });
  }
}

export const api = new ApiClient(API_BASE_URL);
export default api;
