import api from './api';
import type { Bug, ApiResponse, PaginatedResponse } from '@/types';

export const bugService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Bug>>('/bugs', params),

  get: (id: string) =>
    api.get<ApiResponse<Bug>>(`/bugs/${id}`),

  updateStatus: (id: string, status: string) =>
    api.patch<ApiResponse<Bug>>(`/bugs/${id}`, { status }),

  dismiss: (id: string) =>
    api.patch<ApiResponse<Bug>>(`/bugs/${id}`, { status: 'dismissed' }),
};
