from django.urls import path
from . import views

app_name = 'diary'

urlpatterns = [
    path('', views.index, name='index'),
    path('log/', views.scent_log_create, name='scent_log_create'),
    path('<int:pk>/', views.entry_detail, name='entry_detail'),
    path('<int:pk>/edit/', views.scent_log_update, name='scent_log_update'),
    path('<int:pk>/delete/', views.scent_log_delete, name='scent_log_delete'),
]

