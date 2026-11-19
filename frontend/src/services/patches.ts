import api from './api';
import type { Patch, TestRun, ApiResponse, PaginatedResponse } from '@/types';

export const patchService = {
  list: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<Patch>>('/patches', params),

  get: (id: string) =>
    api.get<ApiResponse<Patch>>(`/patches/${id}`),

  approve: (id: string) =>
    api.post<ApiResponse<Patch>>(`/patches/${id}/approve`),

  reject: (id: string, reason?: string) =>
    api.post<ApiResponse<Patch>>(`/patches/${id}/reject`, { reason }),

  createPR: (id: string) =>
    api.post<ApiResponse<Patch>>(`/patches/${id}/create-pr`),

  getTestRun: (patchId: string) =>
    api.get<ApiResponse<TestRun>>(`/patches/${patchId}/test-run`),

  runTests: (patchId: string) =>
    api.post<ApiResponse<TestRun>>(`/patches/${patchId}/run-tests`),

  research: (data: { repositoryId: string; issueNumber?: number; description?: string; targetFile?: string }) =>
    api.post<ApiResponse<any>>('/patches/research', data),

  draft: (data: { repositoryId: string; filePath: string; issueNumber?: number; title?: string; description?: string; userGuidance?: string }) =>
    api.post<ApiResponse<Patch>>('/patches/draft', data),
};
