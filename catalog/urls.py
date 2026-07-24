from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Fragrance catalog routes
    path('', views.index, name='index'),
    path('fragrance/create/', views.fragrance_create, name='fragrance_create'),
    path('fragrance/<int:pk>/', views.fragrance_detail, name='fragrance_detail'),
    path('fragrance/<int:pk>/edit/', views.fragrance_update, name='fragrance_update'),
    path('fragrance/<int:pk>/delete/', views.fragrance_delete, name='fragrance_delete'),

    # Perfume house routes
    path('houses/', views.house_list, name='house_list'),
    path('house/create/', views.house_create, name='house_create'),
    path('house/<int:pk>/', views.house_detail, name='house_detail'),
    path('house/<int:pk>/edit/', views.house_update, name='house_update'),
    path('house/<int:pk>/delete/', views.house_delete, name='house_delete'),

    # Olfactory note routes
    path('notes/', views.note_list, name='note_list'),
    path('note/create/', views.note_create, name='note_create'),
    path('note/<int:pk>/', views.note_detail, name='note_detail'),
    path('note/<int:pk>/edit/', views.note_update, name='note_update'),
    path('note/<int:pk>/delete/', views.note_delete, name='note_delete'),

    # API endpoints
    path('api/search/', views.api_search, name='api_search'),
]