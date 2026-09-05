from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    # Auth
    path('auth/register/', api_views.RegisterView.as_view(), name='api-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),

    # Profile
    path('profile/', api_views.ProfileView.as_view(), name='api-profile'),
    path('profile/edit/', api_views.ProfileUpdateView.as_view(), name='api-profile-edit'),
    path('profile/<str:username>/', api_views.ProfileDetailView.as_view(), name='api-profile-detail'),
    path('profile/<str:username>/follow/', api_views.ToggleFollowView.as_view(), name='api-toggle-follow'),
    path('profile/<str:username>/followers/', api_views.FollowersListView.as_view(), name='api-followers'),
    path('profile/<str:username>/following/', api_views.FollowingListView.as_view(), name='api-following'),

    # Settings
    path('settings/', api_views.UserSettingsView.as_view(), name='api-settings'),

    # Wardrobe
    path('wardrobe/', api_views.WardrobeListView.as_view(), name='api-wardrobe-list'),
    path('wardrobe/add/<int:fragrance_id>/', api_views.WardrobeAddView.as_view(), name='api-wardrobe-add'),
    path('wardrobe/<int:item_id>/', api_views.WardrobeRemoveView.as_view(), name='api-wardrobe-remove'),

    # Feed
    path('feed/', api_views.FeedView.as_view(), name='api-feed'),

    # Export
    path('export/', api_views.ExportDataView.as_view(), name='api-export'),
]
