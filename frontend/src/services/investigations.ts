import api from './api';
import type { Investigation, ApiResponse, PaginatedResponse } from '@/types';

export const investigationService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Investigation>>('/investigations', params),

  get: (id: string) =>
    api.get<ApiResponse<Investigation>>(`/investigations/${id}`),

  create: (data: { question: string; bugId?: string; incidentId?: string; projectId?: string; repositoryId?: string }) =>
    api.post<ApiResponse<Investigation>>('/investigations', data),

  cancel: (id: string) =>
    api.post<ApiResponse<Investigation>>(`/investigations/${id}/cancel`),
};
