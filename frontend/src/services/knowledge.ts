import api from './api';
import type { KnowledgeDocument, RAGSearchResult, RAGAskResponse, ApiResponse, PaginatedResponse } from '@/types';

export const knowledgeService = {
  listDocuments: (params?: Record<string, string>) =>
    api.get<PaginatedResponse<KnowledgeDocument>>('/knowledge/documents', params),

  uploadDocument: (file: File, projectId: string = 'proj_demo_001', sourceType: string = 'documentation') =>
    api.upload<ApiResponse<any>>('/knowledge/upload', file, 'file', {
      projectId,
      sourceType,
    }),

  search: (query: string, projectId?: string, mode?: string, topK?: number) =>
    api.post<ApiResponse<RAGSearchResult[]>>('/knowledge/search', { query, projectId, mode, topK }),

  ask: (query: string, projectId?: string, topK?: number) =>
    api.post<ApiResponse<RAGAskResponse>>('/knowledge/ask', { query, projectId, topK }),

  getEvaluation: () =>
    api.get<ApiResponse<any>>('/knowledge/evaluation'),

  reindex: (documentId: string) =>
    api.post<ApiResponse<void>>(`/knowledge/documents/${documentId}/reindex`),
};
