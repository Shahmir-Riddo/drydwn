from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from catalog.models import Fragrance
from .models import Profile, WardrobeItem, UserSettings
from .forms import SignupForm, EditProfileForm, WardrobeItemForm, UserSettingsForm


def register(request):
    """Register a new user and automatically create their profile."""
    if request.user.is_authenticated:
        return redirect('catalog:index')
        
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to DRYDOWN.')
            return redirect('accounts:profile')
    else:
        form = SignupForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Render authenticated user profile details and activity summary."""
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    wardrobe_count = request.user.wardrobe.count()
    context = {
        'profile': profile_obj,
        'wardrobe_count': wardrobe_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile details."""
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = EditProfileForm(instance=profile_obj)
    return render(request, 'accounts/edit_profile.html', {'form': form})


SETTINGS_SECTIONS = [
    ('Account', ['show_email_on_profile', 'two_factor_enabled', 'language', 'remember_me_default', 'session_timeout_minutes', 'beta_features_enabled']),
    ('Privacy', ['profile_visibility', 'show_wardrobe_publicly', 'show_follower_list', 'allow_follow_requests', 'show_last_active', 'hide_from_search_engines']),
    ('Notifications', ['email_notifications_enabled', 'notify_new_follower', 'notify_comments_likes', 'weekly_digest_email', 'notify_price_drops', 'notify_new_release_in_house', 'push_notifications_enabled']),
    ('Appearance', ['theme', 'compact_wardrobe_view', 'show_ratings_on_cards', 'accent_color', 'font_size', 'reduce_motion']),
    ('Wardrobe Preferences', ['default_shelf', 'bottle_size_unit', 'auto_add_viewed_to_wishlist', 'show_wardrobe_value_estimate', 'default_sort_order', 'show_empty_bottle_alert', 'low_stock_threshold_ml']),
    ('Social', ['allow_tagging', 'show_activity_on_profile', 'discoverable_in_search', 'allow_direct_messages', 'show_wishlist_publicly']),
    ('Data & Export', ['allow_data_export', 'include_wardrobe_in_export', 'diary_retention', 'export_format', 'auto_backup_enabled']),
    ('Security Settings', ['login_alerts_enabled', 'require_password_for_export', 'session_device_list_visible']),
]


@login_required
def settings_view(request):
    """Edit user preference settings across account, privacy, notifications,
    appearance, wardrobe, social, and data & export sections."""
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('accounts:settings')
    else:
        form = UserSettingsForm(instance=settings_obj)

    settings_sections = [
        (title, [form[name] for name in field_names])
        for title, field_names in SETTINGS_SECTIONS
    ]
    return render(request, 'accounts/settings.html', {'form': form, 'settings_sections': settings_sections, 'profile': profile_obj})


@login_required
def wardrobe_index(request):
    """Render the user's wardrobe as a 3D shelf display."""
    queryset = (
        WardrobeItem.objects.filter(user=request.user)
        .select_related('fragrance', 'fragrance__house')
        .order_by('-added_at')
    )

    shelf_items = [
        {
            'name': item.fragrance.name,
            'house': item.fragrance.house.name,
            'imageUrl': reverse('catalog:fragrance_image', kwargs={'pk': item.fragrance.pk}) if item.fragrance.source_image_url else None,
            'detailUrl': reverse('catalog:fragrance_detail', kwargs={'pk': item.fragrance.pk}),
            'shelf': item.shelf,
            'rating': item.personal_rating,
        }
        for item in queryset
    ]

    context = {
        'items': queryset,
        'shelf_items': shelf_items,
    }
    return render(request, 'accounts/wardrobe.html', context)


@login_required
def add_to_wardrobe(request, fragrance_id):
    """Add or update a fragrance in user's wardrobe."""
    fragrance = get_object_or_404(Fragrance, pk=fragrance_id)
    shelf = request.POST.get('shelf', WardrobeItem.ShelfChoices.OWNED)
    
    # Check if shelf choice is valid
    valid_shelves = [choice[0] for choice in WardrobeItem.ShelfChoices.choices]
    if shelf not in valid_shelves:
        shelf = WardrobeItem.ShelfChoices.OWNED

    item, created = WardrobeItem.objects.update_or_create(
        user=request.user,
        fragrance=fragrance,
        defaults={'shelf': shelf}
    )
    
    status_msg = f"Added '{fragrance.name}' to your {shelf} shelf." if created else f"Moved '{fragrance.name}' to your {shelf} shelf."
    messages.success(request, status_msg)
    
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'accounts:wardrobe'
    return redirect(next_url)


@login_required
def remove_from_wardrobe(request, item_id):
    """Remove item from user's wardrobe."""
    item = get_object_or_404(WardrobeItem, pk=item_id, user=request.user)
    fragrance_name = item.fragrance.name
    item.delete()
    messages.success(request, f"Removed '{fragrance_name}' from your wardrobe.")
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'accounts:wardrobe'
    return redirect(next_url)


