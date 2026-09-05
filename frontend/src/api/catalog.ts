import { apiClient } from './client';
import type {
  PaginatedResponse,
  FragranceItem,
  FragranceDetail,
  House,
  Note,
  ReviewItem,
  ReviewsSummary,
  SearchResultItem,
  FragranceRequestItem,
  CommunityInsightCategory,
} from '../types';

export interface FragranceListParams {
  page?: number;
  q?: string;
}

export interface ReviewListResponse {
  summary: ReviewsSummary;
  reviews: ReviewItem[];
  page: number;
  num_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface VoteResponse {
  success: boolean;
  insights: CommunityInsightCategory[];
  total_voters: number;
}

export const catalogApi = {
  getFragrances: async (params?: FragranceListParams): Promise<PaginatedResponse<FragranceItem>> => {
    const res = await apiClient.get<PaginatedResponse<FragranceItem>>('/fragrances/', { params });
    return res.data;
  },

  getFragranceDetail: async (id: number | string): Promise<FragranceDetail> => {
    const res = await apiClient.get<FragranceDetail>(`/fragrances/${id}/`);
    return res.data;
  },

  getFragranceReviews: async (
    id: number | string,
    params?: { page?: number; sort?: 'recent' | 'highest' | 'lowest' | 'helpful' }
  ): Promise<ReviewListResponse> => {
    const res = await apiClient.get<ReviewListResponse>(`/fragrances/${id}/reviews/`, { params });
    return res.data;
  },

  voteFragrance: async (
    id: number | string,
    payload: { category: string; choice: string }
  ): Promise<VoteResponse> => {
    const res = await apiClient.post<VoteResponse>(`/fragrances/${id}/vote/`, payload);
    return res.data;
  },

  search: async (q: string): Promise<{ results: SearchResultItem[] }> => {
    const res = await apiClient.get<{ results: SearchResultItem[] }>('/search/', { params: { q } });
    return res.data;
  },

  getHouses: async (params?: { page?: number; q?: string }): Promise<PaginatedResponse<House>> => {
    const res = await apiClient.get<PaginatedResponse<House>>('/houses/', { params });
    return res.data;
  },

  getHouseDetail: async (id: number | string): Promise<House> => {
    const res = await apiClient.get<House>(`/houses/${id}/`);
    return res.data;
  },

  getNotes: async (params?: { page?: number; q?: string }): Promise<PaginatedResponse<Note>> => {
    const res = await apiClient.get<PaginatedResponse<Note>>('/notes/', { params });
    return res.data;
  },

  getNoteDetail: async (id: number | string): Promise<Note> => {
    const res = await apiClient.get<Note>(`/notes/${id}/`);
    return res.data;
  },

  toggleReviewLike: async (logId: number): Promise<{ success: boolean; liked: boolean; like_count: number }> => {
    const res = await apiClient.post<{ success: boolean; liked: boolean; like_count: number }>(`/reviews/${logId}/like/`);
    return res.data;
  },

  getFragranceRequests: async (): Promise<FragranceRequestItem[]> => {
    const res = await apiClient.get<FragranceRequestItem[]>('/fragrance-requests/');
    return res.data;
  },

  submitFragranceRequest: async (payload: Partial<FragranceRequestItem>): Promise<FragranceRequestItem> => {
    const res = await apiClient.post<FragranceRequestItem>('/fragrance-requests/', payload);
    return res.data;
  },
};
