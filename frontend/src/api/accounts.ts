import { apiClient } from './client';
import type {
  PaginatedResponse,
  UserProfile,
  UserSettings,
  WardrobeItem,
  WardrobeShelf,
  FollowUser,
  FeedItem,
} from '../types';

export interface FeedResponse {
  search_results: FollowUser[];
  feed: FeedItem[];
  discover_users: FollowUser[];
  following_count: number;
}

export interface WardrobeAddPayload {
  shelf: WardrobeShelf;
  personal_rating?: number | null;
  bottle_size_ml?: number | null;
}

export const accountsApi = {
  getMyProfile: async (): Promise<UserProfile> => {
    const res = await apiClient.get<UserProfile>('/profile/');
    return res.data;
  },

  getProfile: async (username: string): Promise<UserProfile> => {
    const res = await apiClient.get<UserProfile>(`/profile/${username}/`);
    return res.data;
  },

  updateProfile: async (
    payload: Partial<Omit<UserProfile, 'favorite_fragrance'>> & {
      email?: string;
      favorite_fragrance?: number | null;
    }
  ): Promise<UserProfile> => {
    const res = await apiClient.patch<UserProfile>('/profile/edit/', payload);
    return res.data;
  },

  getSettings: async (): Promise<UserSettings> => {
    const res = await apiClient.get<UserSettings>('/settings/');
    return res.data;
  },

  updateSettings: async (payload: Partial<UserSettings>): Promise<UserSettings> => {
    const res = await apiClient.patch<UserSettings>('/settings/', payload);
    return res.data;
  },

  getWardrobe: async (params?: { page?: number }): Promise<PaginatedResponse<WardrobeItem>> => {
    const res = await apiClient.get<PaginatedResponse<WardrobeItem>>('/wardrobe/', { params });
    return res.data;
  },

  addToWardrobe: async (
    fragranceId: number,
    payload: WardrobeAddPayload
  ): Promise<{ detail: string; item: WardrobeItem; created: boolean }> => {
    const res = await apiClient.post<{ detail: string; item: WardrobeItem; created: boolean }>(
      `/wardrobe/add/${fragranceId}/`,
      payload
    );
    return res.data;
  },

  removeFromWardrobe: async (itemId: number): Promise<{ detail: string }> => {
    const res = await apiClient.delete<{ detail: string }>(`/wardrobe/${itemId}/`);
    return res.data;
  },

  toggleFollow: async (username: string): Promise<{ detail: string; following: boolean }> => {
    const res = await apiClient.post<{ detail: string; following: boolean }>(`/profile/${username}/follow/`);
    return res.data;
  },

  getFollowers: async (username: string): Promise<FollowUser[]> => {
    const res = await apiClient.get<FollowUser[]>(`/profile/${username}/followers/`);
    return res.data;
  },

  getFollowing: async (username: string): Promise<FollowUser[]> => {
    const res = await apiClient.get<FollowUser[]>(`/profile/${username}/following/`);
    return res.data;
  },

  getFeed: async (params?: { q?: string }): Promise<FeedResponse> => {
    const res = await apiClient.get<FeedResponse>('/feed/', { params });
    return res.data;
  },

  exportData: (format: 'CSV' | 'JSON' = 'CSV'): string => {
    return `/api/v1/export/?format=${format}`;
  },
};
