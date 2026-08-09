import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from catalog.models import Fragrance
from .models import Profile, WardrobeItem, UserSettings, Follow
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


@login_required
def for_you(request):
    """Personalized activity feed of other users' wardrobe adds, ranked by a
    weighted blend of recency decay, follow-graph proximity, and fragrance-taste
    overlap (shared houses/notes) with the viewer's own wardrobe."""
    now = timezone.now()

    following_ids = set(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
    second_degree_ids = set(
        Follow.objects.filter(follower_id__in=following_ids)
        .values_list('following_id', flat=True)
    ) - following_ids - {request.user.id}

    my_wardrobe = (
        WardrobeItem.objects.filter(user=request.user)
        .select_related('fragrance')
        .prefetch_related('fragrance__top_notes', 'fragrance__heart_notes', 'fragrance__base_notes')
    )
    my_house_ids = set()
    my_note_ids = set()
    for w in my_wardrobe:
        my_house_ids.add(w.fragrance.house_id)
        my_note_ids.update(n.id for n in w.fragrance.top_notes.all())
        my_note_ids.update(n.id for n in w.fragrance.heart_notes.all())
        my_note_ids.update(n.id for n in w.fragrance.base_notes.all())

    # Bound the candidate pool to the most recent activity so scoring stays cheap.
    candidates = (
        WardrobeItem.objects
        .exclude(user=request.user)
        .select_related('user__profile', 'fragrance', 'fragrance__house')
        .prefetch_related('fragrance__top_notes', 'fragrance__heart_notes', 'fragrance__base_notes')
        .order_by('-added_at')[:500]
    )

    scored = []
    for item in candidates:
        age_hours = max((now - item.added_at).total_seconds() / 3600, 0)
        recency_score = 100 * math.exp(-age_hours / (24 * 7))

        if item.user_id in following_ids:
            social_score = 60
        elif item.user_id in second_degree_ids:
            social_score = 25
        else:
            social_score = 0

        item_note_ids = (
            {n.id for n in item.fragrance.top_notes.all()}
            | {n.id for n in item.fragrance.heart_notes.all()}
            | {n.id for n in item.fragrance.base_notes.all()}
        )
        shared_notes = len(item_note_ids & my_note_ids)
        house_match = item.fragrance.house_id in my_house_ids
        taste_score = shared_notes * 4 + (12 if house_match else 0)

        rating_score = (item.personal_rating or 0) * 3

        total_score = recency_score + social_score + taste_score + rating_score
        scored.append((total_score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    feed = [item for _, item in scored[:30]]

    return render(request, 'accounts/for_you.html', {'feed': feed})


SETTINGS_SECTIONS = [
    ('Account', ['show_email_on_profile', 'two_factor_enabled', 'language', 'remember_me_default']),
    ('Privacy', ['profile_visibility', 'show_wardrobe_publicly', 'show_follower_list', 'allow_follow_requests']),
    ('Notifications', ['email_notifications_enabled', 'notify_new_follower', 'notify_comments_likes', 'weekly_digest_email']),
    ('Appearance', ['theme', 'compact_wardrobe_view', 'show_ratings_on_cards']),
    ('Wardrobe Preferences', ['default_shelf', 'bottle_size_unit', 'auto_add_viewed_to_wishlist', 'show_wardrobe_value_estimate']),
    ('Social', ['allow_tagging', 'show_activity_on_profile', 'discoverable_in_search']),
    ('Data & Export', ['allow_data_export', 'include_wardrobe_in_export', 'diary_retention']),
]


@login_required
def settings_view(request):
    """Edit user preference settings across account, privacy, notifications,
    appearance, wardrobe, social, and data & export sections."""
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
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
    return render(request, 'accounts/settings.html', {'form': form, 'settings_sections': settings_sections})


@login_required
def wardrobe_index(request):
    """Render user wardrobe collection grouped by shelf category for current user."""
    shelf_filter = request.GET.get('shelf', '')
    user_wardrobe = WardrobeItem.objects.filter(user=request.user)
    queryset = user_wardrobe.select_related('fragrance', 'fragrance__house')
    
    if shelf_filter:
        queryset = queryset.filter(shelf=shelf_filter)

    context = {
        'items': queryset,
        'selected_shelf': shelf_filter,
        'total_count': user_wardrobe.count(),
        'owned_count': user_wardrobe.filter(shelf='Owned').count(),
        'wishlist_count': user_wardrobe.filter(shelf='Wishlist').count(),
        'tried_count': user_wardrobe.filter(shelf='Tried').count(),
        'want_to_try_count': user_wardrobe.filter(shelf='Want to Try').count(),
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


