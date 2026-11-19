import api from './api';
import type { Incident, ApiResponse, PaginatedResponse } from '@/types';

export const incidentService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Incident>>('/incidents', params),

  get: (id: string) =>
    api.get<ApiResponse<Incident>>(`/incidents/${id}`),

  create: (data: Partial<Incident>) =>
    api.post<ApiResponse<Incident>>('/incidents', data),

  update: (id: string, data: Partial<Incident>) =>
    api.patch<ApiResponse<Incident>>(`/incidents/${id}`, data),

  resolve: (id: string) =>
    api.post<ApiResponse<Incident>>(`/incidents/${id}/resolve`),
};
