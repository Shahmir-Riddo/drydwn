from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile_detail'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('feed/', views.feed, name='feed'),
    path('settings/', views.settings_view, name='settings'),
    path('wardrobe/', views.wardrobe_index, name='wardrobe'),
    path('wardrobe/add/<int:fragrance_id>/', views.add_to_wardrobe, name='add_to_wardrobe'),
    path('wardrobe/remove/<int:item_id>/', views.remove_from_wardrobe, name='remove_from_wardrobe'),
]

