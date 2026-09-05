from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import AllUsersPasswordResetForm
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    # Built-in Password Reset Views
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done'),
        form_class=AllUsersPasswordResetForm,
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile_detail'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('feed/', views.feed, name='feed'),
    path('settings/', views.settings_view, name='settings'),
    path('export/', views.export_data, name='export_data'),
    path('wardrobe/', views.wardrobe_index, name='wardrobe'),
    path('wardrobe/add/<int:fragrance_id>/', views.add_to_wardrobe, name='add_to_wardrobe'),
    path('wardrobe/remove/<int:item_id>/', views.remove_from_wardrobe, name='remove_from_wardrobe'),
]

