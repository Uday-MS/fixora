import api from './api';
import type { Repository, RepositoryFile, ApiResponse, PaginatedResponse } from '@/types';

export const repositoryService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Repository>>('/repositories', params),

  get: (id: string) =>
    api.get<ApiResponse<Repository>>(`/repositories/${id}`),

  connect: (data: { url: string; branch?: string; token?: string }) =>
    api.post<ApiResponse<Repository>>('/repositories', data),

  sync: (id: string) =>
    api.post<ApiResponse<Repository>>(`/repositories/${id}/sync`),

  getFiles: (id: string) =>
    api.get<ApiResponse<RepositoryFile[]>>(`/repositories/${id}/files`),

  delete: (id: string) =>
    api.delete<void>(`/repositories/${id}`),

  upload: (file: File, projectId: string) =>
    api.upload<ApiResponse<Repository>>(`/repositories/upload?projectId=${projectId}`, file),

  uploadZip: (repositoryId: string, file: File) =>
    api.upload<ApiResponse<any>>(`/repositories/${repositoryId}/upload-zip`, file),

  uploadStandaloneZip: (file: File, name?: string, projectId?: string) =>
    api.upload<ApiResponse<any>>('/repositories/upload-zip', file, 'file', {
      name: name || '',
      projectId: projectId || '',
    }),
};
