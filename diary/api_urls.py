from django.urls import path
from . import api_views

urlpatterns = [
    path('diary/', api_views.ScentLogListCreateView.as_view(), name='api-diary-list'),
    path('diary/<int:pk>/', api_views.ScentLogDetailView.as_view(), name='api-diary-detail'),
]
