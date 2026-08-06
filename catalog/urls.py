from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Fragrance detail (read-only)
    path('fragrance/<int:pk>/', views.fragrance_detail, name='fragrance_detail'),
    # House list and detail (read-only)
    path('houses/', views.house_list, name='house_list'),
    path('house/<int:pk>/', views.house_detail, name='house_detail'),
    # Note list and detail (read-only)
    path('notes/', views.note_list, name='note_list'),
    path('note/<int:pk>/', views.note_detail, name='note_detail'),
    # API endpoint
    path('api/search/', views.api_search, name='api_search'),
]