import { apiClient } from './client';
import type { PaginatedResponse, ScentLog, ScentLogFormValues } from '../types';

export const diaryApi = {
  getLogs: async (params?: { page?: number }): Promise<PaginatedResponse<ScentLog>> => {
    const res = await apiClient.get<PaginatedResponse<ScentLog>>('/diary/', { params });
    return res.data;
  },

  getLogDetail: async (id: number | string): Promise<ScentLog> => {
    const res = await apiClient.get<ScentLog>(`/diary/${id}/`);
    return res.data;
  },

  createLog: async (payload: ScentLogFormValues): Promise<ScentLog> => {
    const res = await apiClient.post<ScentLog>('/diary/', payload);
    return res.data;
  },

  updateLog: async (id: number | string, payload: Partial<ScentLogFormValues>): Promise<ScentLog> => {
    const res = await apiClient.patch<ScentLog>(`/diary/${id}/`, payload);
    return res.data;
  },

  deleteLog: async (id: number | string): Promise<void> => {
    await apiClient.delete(`/diary/${id}/`);
  },
};
