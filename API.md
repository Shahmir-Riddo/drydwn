# Drydown REST API Documentation (v1)

This document provides complete documentation for the Drydown REST API (`/api/v1/`). It serves as the single source of truth for the React web SPA and React Native mobile applications.

---

## 1. Overview & Architecture

- **Base URL**: `/api/v1/`
- **Content Type**: `application/json`
- **Authentication**: JWT Bearer Tokens via SimpleJWT (`Authorization: Bearer <access_token>`)
- **CORS**: Configured for React dev server (`http://localhost:5173`, `http://localhost:3000`) and production frontends.

---

## 2. Authentication Flow

### Obtain Token (Login)
- **Endpoint**: `POST /api/v1/auth/token/`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "curator_user",
    "password": "curator_password"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
  }
  ```

### Refresh Token
- **Endpoint**: `POST /api/v1/auth/token/refresh/`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
  }
  ```

### Register
- **Endpoint**: `POST /api/v1/auth/register/`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "new_curator",
    "email": "curator@example.com",
    "password": "secure_password_123",
    "password_confirm": "secure_password_123"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "detail": "Verification email sent to curator@example.com. Please check your inbox to activate your account."
  }
  ```

---

## 3. Catalog Endpoints

### List Fragrances
- **Endpoint**: `GET /api/v1/fragrances/`
- **Auth Required**: Optional (personalizes order when authenticated)
- **Query Parameters**:
  - `page`: Page number (default: `1`, 24 items per page)
  - `q`: Search query string by fragrance name or house name
- **Response** (`200 OK`):
  ```json
  {
    "count": 24800,
    "next": "http://localhost:8000/api/v1/fragrances/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Aventus",
        "house": {
          "id": 4,
          "name": "Creed"
        },
        "gender": "Men",
        "release_year": 2010,
        "image_url": "http://localhost:8000/fragrance/1/image/"
      }
    ]
  }
  ```

### Fragrance Detail
- **Endpoint**: `GET /api/v1/fragrances/{id}/`
- **Auth Required**: Optional
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "name": "Aventus",
    "house": {
      "id": 4,
      "name": "Creed"
    },
    "gender": "Men",
    "release_year": 2010,
    "image_url": "http://localhost:8000/fragrance/1/image/",
    "top_notes": [
      { "id": 10, "name": "Bergamot" },
      { "id": 11, "name": "Blackcurrant" },
      { "id": 12, "name": "Pineapple" },
      { "id": 13, "name": "Apple" }
    ],
    "heart_notes": [
      { "id": 14, "name": "Birch" },
      { "id": 15, "name": "Patchouli" },
      { "id": 16, "name": "Moroccan Jasmine" },
      { "id": 17, "name": "Rose" }
    ],
    "base_notes": [
      { "id": 18, "name": "Musk" },
      { "id": 19, "name": "Oakmoss" },
      { "id": 20, "name": "Ambergris" },
      { "id": 21, "name": "Vanille" }
    ],
    "current_shelf": "Owned",
    "wardrobe_item_id": 42,
    "community_insights": [
      {
        "key": "time_of_day",
        "title": "Best time of day",
        "total_votes": 350,
        "options": [
          { "name": "Daytime", "count": 180, "percentage": 51.4, "is_user_choice": true },
          { "name": "Evening", "count": 100, "percentage": 28.6, "is_user_choice": false },
          { "name": "Night out", "count": 50, "percentage": 14.3, "is_user_choice": false },
          { "name": "Office", "count": 20, "percentage": 5.7, "is_user_choice": false }
        ],
        "user_choice": "Daytime"
      },
      {
        "key": "season",
        "title": "Best season to wear",
        "total_votes": 320,
        "options": [
          { "name": "Spring", "count": 140, "percentage": 43.8, "is_user_choice": false },
          { "name": "Summer", "count": 110, "percentage": 34.4, "is_user_choice": false },
          { "name": "Fall", "count": 50, "percentage": 15.6, "is_user_choice": false },
          { "name": "Winter", "count": 20, "percentage": 6.2, "is_user_choice": false }
        ],
        "user_choice": null
      },
      {
        "key": "longevity",
        "title": "Longevity",
        "total_votes": 290,
        "options": [
          { "name": "Very weak", "count": 5, "percentage": 1.7, "is_user_choice": false },
          { "name": "Weak", "count": 25, "percentage": 8.6, "is_user_choice": false },
          { "name": "Moderate", "count": 110, "percentage": 37.9, "is_user_choice": false },
          { "name": "Long lasting", "count": 120, "percentage": 41.4, "is_user_choice": false },
          { "name": "Eternal", "count": 30, "percentage": 10.3, "is_user_choice": false }
        ],
        "user_choice": null
      },
      {
        "key": "projection",
        "title": "Projection",
        "total_votes": 280,
        "options": [
          { "name": "Soft", "count": 15, "percentage": 5.4, "is_user_choice": false },
          { "name": "Moderate", "count": 130, "percentage": 46.4, "is_user_choice": false },
          { "name": "Strong", "count": 115, "percentage": 41.1, "is_user_choice": false },
          { "name": "Enormous", "count": 20, "percentage": 7.1, "is_user_choice": false }
        ],
        "user_choice": null
      }
    ],
    "total_voters": 410,
    "reviews_summary": {
      "avg_rating": 4.6,
      "total_reviews": 85,
      "total_ratings_count": 120,
      "star_breakdown": [
        { "stars": 5, "count": 75, "percentage": 62.5 },
        { "stars": 4, "count": 30, "percentage": 25.0 },
        { "stars": 3, "count": 10, "percentage": 8.3 },
        { "stars": 2, "count": 3, "percentage": 2.5 },
        { "stars": 1, "count": 2, "percentage": 1.7 }
      ]
    }
  }
  ```

### Fragrance Reviews (Paginated)
- **Endpoint**: `GET /api/v1/fragrances/{id}/reviews/`
- **Auth Required**: Optional (populates `is_liked_by_user` and `is_author` if authenticated)
- **Query Parameters**:
  - `page`: Page number (default: `1`, 10 items per page)
  - `sort`: `recent` (default), `highest`, `lowest`, or `helpful`
- **Response** (`200 OK`):
  ```json
  {
    "summary": {
      "avg_rating": 4.6,
      "total_reviews": 85,
      "total_ratings_count": 120,
      "star_breakdown": [ ... ]
    },
    "reviews": [
      {
        "id": 15,
        "user_name": "Alexander V.",
        "username": "alexv",
        "avatar_url": "https://images.unsplash.com/...",
        "initials": "AV",
        "rating": "4.5",
        "wear_date": "2026-08-15",
        "occasion": "Special Occasion",
        "review_text": "Incredible pineapple and birch drydown.",
        "review_title": "Incredible pineapple and birch drydown",
        "descriptor_tags": [
          "Strong Projection",
          "Long Lasting",
          "Special Occasion Wear",
          "Standout Choice"
        ],
        "like_count": 12,
        "is_liked_by_user": true,
        "is_author": false,
        "is_favorite": true,
        "sprays": 4,
        "sillage_rating": 4,
        "longevity_hours": 9,
        "created_at": "2026-08-15T18:30:00Z"
      }
    ],
    "page": 1,
    "num_pages": 9,
    "has_next": true,
    "has_previous": false
  }
  ```

### Fragrance Community Vote
- **Endpoint**: `POST /api/v1/fragrances/{id}/vote/`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "category": "time_of_day",
    "choice": "Evening"
  }
  ```
  *Allowed categories & choices:*
  - `time_of_day`: `Daytime`, `Evening`, `Night out`, `Office`
  - `season`: `Spring`, `Summer`, `Fall`, `Winter`
  - `longevity`: `Very weak`, `Weak`, `Moderate`, `Long lasting`, `Eternal`
  - `projection`: `Soft`, `Moderate`, `Strong`, `Enormous`
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "insights": [ ... ],
    "total_voters": 411
  }
  ```

### Autocomplete Search
- **Endpoint**: `GET /api/v1/search/`
- **Auth Required**: No
- **Query Parameters**: `q` (e.g. `?q=avent`)
- **Response** (`200 OK`):
  ```json
  {
    "results": [
      {
        "id": 1,
        "name": "Aventus",
        "house": "Creed",
        "image_url": "http://localhost:8000/fragrance/1/image/"
      }
    ]
  }
  ```

### List Houses
- **Endpoint**: `GET /api/v1/houses/`
- **Auth Required**: No
- **Query Parameters**:
  - `page`: Page number (default: `1`, 30 per page)
  - `q`: Filter by house name
- **Response** (`200 OK`):
  ```json
  {
    "count": 450,
    "next": "http://localhost:8000/api/v1/houses/?page=2",
    "previous": null,
    "results": [
      {
        "id": 4,
        "name": "Creed",
        "fragrance_count": 82
      }
    ]
  }
  ```

### House Detail
- **Endpoint**: `GET /api/v1/houses/{id}/`
- **Auth Required**: No
- **Response** (`200 OK`):
  ```json
  {
    "id": 4,
    "name": "Creed",
    "created_at": "2026-01-01T00:00:00Z",
    "fragrances": [
      {
        "id": 1,
        "name": "Aventus",
        "house_name": "Creed",
        "gender": "Men",
        "release_year": 2010,
        "image_url": "http://localhost:8000/fragrance/1/image/"
      }
    ]
  }
  ```

### List Notes
- **Endpoint**: `GET /api/v1/notes/`
- **Auth Required**: No
- **Query Parameters**: `page` (50/page), `q`
- **Response** (`200 OK`):
  ```json
  {
    "count": 1200,
    "next": "http://localhost:8000/api/v1/notes/?page=2",
    "previous": null,
    "results": [
      {
        "id": 10,
        "name": "Bergamot"
      }
    ]
  }
  ```

### Note Detail
- **Endpoint**: `GET /api/v1/notes/{id}/`
- **Auth Required**: No
- **Response** (`200 OK`):
  ```json
  {
    "id": 10,
    "name": "Bergamot"
  }
  ```

### Toggle Review Like (Helpful Vote)
- **Endpoint**: `POST /api/v1/reviews/{id}/like/`
- **Auth Required**: Yes
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "liked": true,
    "like_count": 13
  }
  ```

### Fragrance Requests (Community Submission)
- **Endpoint**: `GET /api/v1/fragrance-requests/` | `POST /api/v1/fragrance-requests/`
- **Auth Required**: Yes
- **POST Body**:
  ```json
  {
    "fragrance_name": "Grand Soir",
    "house_name": "Maison Francis Kurkdjian",
    "gender": "Unisex",
    "release_year": 2016,
    "notes_description": "Amber, vanilla, tonka bean, benzoin, labdanum",
    "reference_url": "https://www.fragrantica.com/perfume/Maison-Francis-Kurkdjian/Grand-Soir-40816.html"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": 8,
    "username": "alexv",
    "fragrance_name": "Grand Soir",
    "house_name": "Maison Francis Kurkdjian",
    "gender": "Unisex",
    "release_year": 2016,
    "notes_description": "Amber, vanilla, tonka bean, benzoin, labdanum",
    "reference_url": "https://www.fragrantica.com/perfume/Maison-Francis-Kurkdjian/Grand-Soir-40816.html",
    "status": "Pending",
    "upvotes": 0,
    "created_at": "2026-09-01T14:00:00Z"
  }
  ```

---

## 4. Diary Endpoints (Wear Logs)

### List Own Diary Entries
- **Endpoint**: `GET /api/v1/diary/`
- **Auth Required**: Yes
- **Query Parameters**: `page` (default: 24/page)
- **Response** (`200 OK`):
  ```json
  {
    "count": 48,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 101,
        "fragrance_id": 1,
        "fragrance_name": "Aventus",
        "house_name": "Creed",
        "wear_date": "2026-09-01",
        "rating": "4.5",
        "occasion": "Work",
        "sprays": 3,
        "sillage_rating": 4,
        "longevity_hours": 8,
        "is_favorite": false,
        "like_count": 0,
        "created_at": "2026-09-01T08:00:00Z"
      }
    ]
  }
  ```

### Create Diary Entry
- **Endpoint**: `POST /api/v1/diary/`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "fragrance": 1,
    "wear_date": "2026-09-01",
    "rating": 4.5,
    "occasion": "Work",
    "sprays": 3,
    "sillage_rating": 4,
    "longevity_hours": 8,
    "review_text": "Great morning performance, compliments at lunch.",
    "is_favorite": false
  }
  ```
  *Note: `fragrance` ID must exist in the user's wardrobe.*
- **Response** (`201 Created`):
  ```json
  {
    "id": 102,
    "fragrance": 1,
    "wear_date": "2026-09-01",
    "rating": "4.5",
    "occasion": "Work",
    "sprays": 3,
    "sillage_rating": 4,
    "longevity_hours": 8,
    "review_text": "Great morning performance, compliments at lunch.",
    "is_favorite": false
  }
  ```

### Retrieve / Update / Delete Diary Entry
- **Endpoint**: `GET /api/v1/diary/{id}/` | `PUT /api/v1/diary/{id}/` | `PATCH /api/v1/diary/{id}/` | `DELETE /api/v1/diary/{id}/`
- **Auth Required**: Yes
- **Permissions**: Safe methods (GET) accessible to authenticated users; PUT/PATCH/DELETE restricted strictly to the entry owner or staff.
- **GET Response** (`200 OK`):
  ```json
  {
    "id": 101,
    "username": "alexv",
    "fragrance_id": 1,
    "fragrance_name": "Aventus",
    "house_name": "Creed",
    "wear_date": "2026-09-01",
    "rating": "4.5",
    "occasion": "Work",
    "sprays": 3,
    "sillage_rating": 4,
    "longevity_hours": 8,
    "review_text": "Great morning performance.",
    "is_favorite": false,
    "like_count": 2,
    "created_at": "2026-09-01T08:00:00Z"
  }
  ```
- **DELETE Response** (`204 No Content`)

---

## 5. Accounts & Social Endpoints

### Own Profile
- **Endpoint**: `GET /api/v1/profile/`
- **Auth Required**: Yes
- **Response** (`200 OK`):
  ```json
  {
    "username": "alexv",
    "display_name": "Alexander V.",
    "bio": "Curating niche scents since 2018.",
    "avatar_url": "https://images.unsplash.com/...",
    "location": "Paris, France",
    "favorite_fragrance": {
      "id": 1,
      "name": "Aventus",
      "house": "Creed"
    },
    "follower_count": 45,
    "following_count": 32,
    "is_following": false,
    "created_at": "2026-01-10T12:00:00Z"
  }
  ```

### Other User's Profile
- **Endpoint**: `GET /api/v1/profile/{username}/`
- **Auth Required**: Optional
- **Response** (`200 OK`): Same shape as above (`is_following` dynamically computed relative to caller).

### Edit Profile
- **Endpoint**: `PUT /api/v1/profile/edit/` | `PATCH /api/v1/profile/edit/`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "display_name": "Alexander V.",
    "bio": "Updated olfactory bio.",
    "location": "Grasse, France",
    "avatar_url": "https://images.unsplash.com/...",
    "favorite_fragrance": 1,
    "email": "curator@example.com"
  }
  ```

### User Settings
- **Endpoint**: `GET /api/v1/settings/` | `PUT /api/v1/settings/` | `PATCH /api/v1/settings/`
- **Auth Required**: Yes
- **Response** (`200 OK`):
  ```json
  {
    "show_email_on_profile": false,
    "two_factor_enabled": false,
    "language": "English",
    "remember_me_default": true,
    "session_timeout_minutes": "60",
    "beta_features_enabled": false,
    "profile_visibility": "Public",
    "show_wardrobe_publicly": true,
    "show_follower_list": true,
    "allow_follow_requests": true,
    "show_last_active": true,
    "hide_from_search_engines": false,
    "email_notifications_enabled": true,
    "notify_new_follower": true,
    "notify_comments_likes": true,
    "weekly_digest_email": false,
    "notify_price_drops": false,
    "notify_new_release_in_house": false,
    "push_notifications_enabled": true,
    "theme": "Auto",
    "compact_wardrobe_view": false,
    "show_ratings_on_cards": true,
    "accent_color": "Brass",
    "font_size": "Medium",
    "reduce_motion": false,
    "default_shelf": "Owned",
    "bottle_size_unit": "ML",
    "auto_add_viewed_to_wishlist": false,
    "show_wardrobe_value_estimate": false,
    "default_sort_order": "Recently Added",
    "show_empty_bottle_alert": true,
    "low_stock_threshold_ml": 10,
    "allow_tagging": true,
    "show_activity_on_profile": true,
    "discoverable_in_search": true,
    "allow_direct_messages": true,
    "show_wishlist_publicly": true,
    "allow_data_export": true,
    "include_wardrobe_in_export": true,
    "diary_retention": "Never",
    "export_format": "CSV",
    "auto_backup_enabled": false,
    "login_alerts_enabled": true,
    "require_password_for_export": false,
    "session_device_list_visible": true
  }
  ```

### Wardrobe List
- **Endpoint**: `GET /api/v1/wardrobe/`
- **Auth Required**: Yes
- **Response** (`200 OK`):
  ```json
  {
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 42,
        "fragrance_id": 1,
        "fragrance_name": "Aventus",
        "house_name": "Creed",
        "shelf": "Owned",
        "personal_rating": 5,
        "bottle_size_ml": 100,
        "has_image": true,
        "added_at": "2026-02-01T10:00:00Z"
      }
    ]
  }
  ```

### Add/Update Wardrobe Shelf
- **Endpoint**: `POST /api/v1/wardrobe/add/{fragrance_id}/`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "shelf": "Owned",
    "personal_rating": 5,
    "bottle_size_ml": 100
  }
  ```
  *Allowed `shelf` values: `Owned`, `Wishlist`, `Tried`, `Want to Try`*
- **Response** (`200 OK` or `201 Created`):
  ```json
  {
    "detail": "Fragrance 'Aventus' added on your Owned shelf.",
    "item": {
      "id": 42,
      "fragrance_id": 1,
      "fragrance_name": "Aventus",
      "house_name": "Creed",
      "shelf": "Owned",
      "personal_rating": 5,
      "bottle_size_ml": 100,
      "has_image": true,
      "added_at": "2026-09-01T14:30:00Z"
    },
    "created": true
  }
  ```

### Remove Wardrobe Item
- **Endpoint**: `DELETE /api/v1/wardrobe/{item_id}/`
- **Auth Required**: Yes (strictly owner)
- **Response** (`200 OK`):
  ```json
  {
    "detail": "Removed 'Aventus' from your wardrobe."
  }
  ```

### Follow / Unfollow User
- **Endpoint**: `POST /api/v1/profile/{username}/follow/`
- **Auth Required**: Yes
- **Response** (`200 OK`):
  ```json
  {
    "detail": "Now following @johndoe.",
    "following": true
  }
  ```

### Followers List
- **Endpoint**: `GET /api/v1/profile/{username}/followers/`
- **Auth Required**: Yes
- **Response** (`200 OK`):
  ```json
  [
    {
      "username": "johndoe",
      "display_name": "John Doe",
      "avatar_url": "",
      "bio": "Fragrance explorer.",
      "is_following": false,
      "is_me": false
    }
  ]
  ```

### Following List
- **Endpoint**: `GET /api/v1/profile/{username}/following/`
- **Auth Required**: Yes
- **Response** (`200 OK`): Same shape as above.

### Feed & Discovery
- **Endpoint**: `GET /api/v1/feed/`
- **Auth Required**: Yes
- **Query Parameters**: `q` (optional member search)
- **Response** (`200 OK`):
  ```json
  {
    "search_results": [],
    "feed": [
      {
        "type": "wear",
        "username": "alexv",
        "display_name": "Alexander V.",
        "avatar_url": "https://...",
        "fragrance_id": 1,
        "fragrance_name": "Aventus",
        "house_name": "Creed",
        "timestamp": "2026-09-01T08:00:00Z",
        "shelf": null,
        "rating": "4.5",
        "occasion": "Work"
      }
    ],
    "discover_users": [
      {
        "username": "sarah_scents",
        "display_name": "Sarah S.",
        "avatar_url": "",
        "bio": "Gourmand lover.",
        "is_following": false,
        "is_me": false
      }
    ],
    "following_count": 12
  }
  ```

### Export Data (CSV or JSON)
- **Endpoint**: `GET /api/v1/export/?format=JSON` (or `?format=CSV`)
- **Auth Required**: Yes
- **Response**: File download (`application/json` or `text/csv`) containing user's wardrobe collection and scent diary logs.
