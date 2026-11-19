import api from './api';
import type { DashboardStats, ApiResponse } from '@/types';

export const dashboardService = {
  getStats: () =>
    api.get<ApiResponse<DashboardStats>>('/dashboard/stats'),
};
