from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Request a perfume
    path('request/', views.request_fragrance, name='request_fragrance'),
    # Fragrance detail & actions
    path('fragrance/<int:pk>/', views.fragrance_detail, name='fragrance_detail'),
    path('fragrance/<int:pk>/image/', views.fragrance_image, name='fragrance_image'),
    path('fragrance/<int:pk>/vote/', views.vote_fragrance, name='fragrance_vote'),
    path('fragrance/<int:pk>/reviews/', views.load_reviews, name='fragrance_reviews'),
    path('reviews/<int:log_id>/like/', views.toggle_like_review, name='toggle_like_review'),
    # House list and detail (read-only)
    path('houses/', views.house_list, name='house_list'),
    path('house/<int:pk>/', views.house_detail, name='house_detail'),
    # Note list and detail (read-only)
    path('notes/', views.note_list, name='note_list'),
    path('note/<int:pk>/', views.note_detail, name='note_detail'),
    # API endpoint
    path('api/search/', views.api_search, name='api_search'),
    path('api/load-more/', views.load_more_fragrances, name='load_more_fragrances'),
]