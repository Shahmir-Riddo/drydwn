from django.urls import path
from . import api_views

urlpatterns = [
    # Fragrances
    path('fragrances/', api_views.FragranceListView.as_view(), name='api-fragrance-list'),
    path('fragrances/<int:pk>/', api_views.FragranceDetailView.as_view(), name='api-fragrance-detail'),
    path('fragrances/<int:pk>/reviews/', api_views.FragranceReviewsView.as_view(), name='api-fragrance-reviews'),
    path('fragrances/<int:pk>/vote/', api_views.FragranceVoteView.as_view(), name='api-fragrance-vote'),

    # Search
    path('search/', api_views.FragranceSearchView.as_view(), name='api-search'),

    # Houses
    path('houses/', api_views.HouseListView.as_view(), name='api-house-list'),
    path('houses/<int:pk>/', api_views.HouseDetailView.as_view(), name='api-house-detail'),

    # Notes
    path('notes/', api_views.NoteListView.as_view(), name='api-note-list'),
    path('notes/<int:pk>/', api_views.NoteDetailView.as_view(), name='api-note-detail'),

    # Review actions
    path('reviews/<int:log_id>/like/', api_views.ToggleLikeView.as_view(), name='api-toggle-like'),

    # Fragrance requests
    path('fragrance-requests/', api_views.FragranceRequestListCreateView.as_view(), name='api-fragrance-requests'),
]
