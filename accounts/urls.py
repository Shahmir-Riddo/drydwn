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
    path('settings/', views.settings_view, name='settings'),
    path('for-you/', views.for_you, name='for_you'),
    path('wardrobe/', views.wardrobe_index, name='wardrobe'),
    path('wardrobe/add/<int:fragrance_id>/', views.add_to_wardrobe, name='add_to_wardrobe'),
    path('wardrobe/remove/<int:item_id>/', views.remove_from_wardrobe, name='remove_from_wardrobe'),
]

