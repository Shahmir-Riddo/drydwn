export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Note {
  id: number;
  name: string;
}

export interface House {
  id: number;
  name: string;
  fragrance_count?: number;
  created_at?: string;
  fragrances?: FragranceMinimal[];
}

export interface FragranceMinimal {
  id: number;
  name: string;
  house_name: string;
  gender: string;
  release_year: number | null;
  image_url: string | null;
  thumbnail_url?: string | null;
}

export interface FragranceItem {
  id: number;
  name: string;
  house: {
    id: number;
    name: string;
  };
  gender: 'Men' | 'Women' | 'Unisex';
  release_year: number | null;
  image_url: string | null;
  thumbnail_url?: string | null;
}

export interface CommunityInsightOption {
  name: string;
  count: number;
  percentage: number;
  is_user_choice: boolean;
}

export interface CommunityInsightCategory {
  key: string;
  title: string;
  total_votes: number;
  options: CommunityInsightOption[];
  user_choice: string | null;
}

export interface StarBreakdown {
  stars: number;
  count: number;
  percentage: number;
}

export interface ReviewsSummary {
  avg_rating: number;
  total_reviews: number;
  total_ratings_count: number;
  star_breakdown: StarBreakdown[];
}

export interface ReviewItem {
  id: number;
  user_name: string;
  username: string;
  avatar_url: string;
  initials: string;
  rating: string | number | null;
  wear_date: string;
  occasion: string;
  review_text: string;
  review_title: string;
  descriptor_tags: string[];
  like_count: number;
  is_liked_by_user: boolean;
  is_author: boolean;
  is_favorite: boolean;
  sprays: number;
  sillage_rating: number | null;
  longevity_hours: number | null;
  created_at: string;
}

export interface FragranceDetail extends FragranceItem {
  top_notes: Note[];
  heart_notes: Note[];
  base_notes: Note[];
  current_shelf: string | null;
  wardrobe_item_id: number | null;
  community_insights: CommunityInsightCategory[];
  total_voters: number;
  reviews_summary: ReviewsSummary;
}

export interface FragranceVotePayload {
  category: 'time_of_day' | 'season' | 'longevity' | 'projection';
  choice: string;
}

export interface ScentLog {
  id: number;
  username?: string;
  fragrance_id: number;
  fragrance_name: string;
  house_name: string;
  wear_date: string;
  rating: string | number | null;
  occasion: string;
  sprays: number;
  sillage_rating: number | null;
  longevity_hours: number | null;
  review_text?: string;
  is_favorite: boolean;
  like_count: number;
  created_at: string;
}

export interface ScentLogFormValues {
  fragrance: number;
  wear_date: string;
  rating?: number | null;
  occasion?: string;
  sprays: number;
  sillage_rating?: number | null;
  longevity_hours?: number | null;
  review_text?: string;
  is_favorite: boolean;
}

export type WardrobeShelf = 'Owned' | 'Wishlist' | 'Tried' | 'Want to Try';

export interface WardrobeItem {
  id: number;
  fragrance_id: number;
  fragrance_name: string;
  house_name: string;
  shelf: WardrobeShelf;
  personal_rating: number | null;
  bottle_size_ml: number | null;
  has_image: boolean;
  added_at: string;
}

export interface UserProfile {
  username: string;
  display_name: string;
  bio: string;
  avatar_url: string;
  location: string;
  favorite_fragrance: {
    id: number;
    name: string;
    house: string | null;
  } | null;
  follower_count: number;
  following_count: number;
  is_following: boolean;
  created_at: string;
}

export interface UserSettings {
  show_email_on_profile: boolean;
  two_factor_enabled: boolean;
  language: string;
  remember_me_default: boolean;
  session_timeout_minutes: string;
  beta_features_enabled: boolean;
  profile_visibility: string;
  show_wardrobe_publicly: boolean;
  show_follower_list: boolean;
  allow_follow_requests: boolean;
  show_last_active: boolean;
  hide_from_search_engines: boolean;
  email_notifications_enabled: boolean;
  notify_new_follower: boolean;
  notify_comments_likes: boolean;
  weekly_digest_email: boolean;
  notify_price_drops: boolean;
  notify_new_release_in_house: boolean;
  push_notifications_enabled: boolean;
  theme: string;
  compact_wardrobe_view: boolean;
  show_ratings_on_cards: boolean;
  accent_color: string;
  font_size: string;
  reduce_motion: boolean;
  default_shelf: string;
  bottle_size_unit: string;
  auto_add_viewed_to_wishlist: boolean;
  show_wardrobe_value_estimate: boolean;
  default_sort_order: string;
  show_empty_bottle_alert: boolean;
  low_stock_threshold_ml: number;
  allow_tagging: boolean;
  show_activity_on_profile: boolean;
  discoverable_in_search: boolean;
  allow_direct_messages: boolean;
  show_wishlist_publicly: boolean;
  allow_data_export: boolean;
  include_wardrobe_in_export: boolean;
  diary_retention: string;
  export_format: string;
  auto_backup_enabled: boolean;
  login_alerts_enabled: boolean;
  require_password_for_export: boolean;
  session_device_list_visible: boolean;
}

export interface FollowUser {
  username: string;
  display_name: string;
  avatar_url: string;
  bio: string;
  is_following: boolean;
  is_me: boolean;
}

export interface FeedItem {
  type: 'wardrobe' | 'wear';
  username: string;
  display_name: string;
  avatar_url: string;
  fragrance_id: number;
  fragrance_name: string;
  house_name: string | null;
  timestamp: string;
  shelf?: string | null;
  rating?: string | number | null;
  occasion?: string | null;
}

export interface FragranceRequestItem {
  id: number;
  username: string;
  fragrance_name: string;
  house_name: string;
  gender: string;
  release_year: number | null;
  notes_description: string;
  reference_url: string;
  status: string;
  upvotes: number;
  created_at: string;
}

export interface SearchResultItem {
  id: number;
  name: string;
  house: string;
  image_url: string | null;
  thumbnail_url?: string | null;
}
