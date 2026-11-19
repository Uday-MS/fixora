function resolveApiBaseUrl(): string {
  // If explicitly configured during build or runtime
  if (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL.trim()) {
    return import.meta.env.VITE_API_URL.trim();
  }
  // When running on Render in production without VITE_API_URL, default directly to the actual production backend
  if (typeof window !== 'undefined' && window.location.hostname.includes('render.com')) {
    return 'https://fixora-api-a2an.onrender.com/api';
  }
  // Local development default (proxied via Vite dev server)
  return '/api';
}

const API_BASE_URL = resolveApiBaseUrl();

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

  getBaseUrl(): string {
    return this.baseUrl;
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
        const errData = await response.json().catch(() => ({ message: response.statusText || `Request failed (HTTP ${response.status})` }));
        throw new ApiError(errData.detail || errData.message || `Request failed (HTTP ${response.status})`, response.status);
      }
      if (response.status === 204) return {} as T;
      return await response.json();
    } catch (err: any) {
      if (err instanceof ApiError) throw err;
      const isNetworkError = err?.name === 'TypeError' || err?.message === 'Failed to fetch';
      const detailMsg = isNetworkError
        ? `Network connection error: Unable to communicate with FIXORA API at ${this.baseUrl}. Please check internet connectivity or service availability.`
        : (err?.message || 'Network error connecting to Fixora backend');
      throw new ApiError(detailMsg, 503);
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
    const url = `${this.baseUrl}${endpoint}`;
    return fetch(url, {
      method: 'POST',
      body: formData,
      headers,
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `Upload failed (HTTP ${res.status}: ${res.statusText})` }));
        throw new ApiError(err.detail || err.message || `Upload failed (HTTP ${res.status})`, res.status);
      }
      return res.json() as Promise<T>;
    }).catch((err: any) => {
      if (err instanceof ApiError) throw err;
      const isNetworkError = err?.name === 'TypeError' || err?.message === 'Failed to fetch';
      const detailMsg = isNetworkError
        ? `Network connection error: Unable to upload file to FIXORA API at ${url}. Please check service availability.`
        : (err?.message || 'Upload failed due to network error');
      throw new ApiError(detailMsg, 503);
    });
  }
}

export const api = new ApiClient(API_BASE_URL);
export default api;
