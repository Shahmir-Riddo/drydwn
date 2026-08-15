from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q, Count
from catalog.models import Fragrance
from diary.models import ScentLog
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


def profile(request, username=None):
    """Render a user's profile (own profile if username=None)."""
    if username is None:
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
        
    profile_obj, _ = Profile.objects.get_or_create(user=user)
    
    # Check if the viewer follows this user
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        
    wardrobe_count = user.wardrobe.count()
    
    # Wardrobe Shelf Display (3D shelf items format)
    queryset = (
        WardrobeItem.objects.filter(user=user)
        .select_related('fragrance', 'fragrance__house')
        .order_by('-added_at')
    )
    shelf_items = [
        {
            'id': item.id,
            'name': item.fragrance.name,
            'house': item.fragrance.house.name,
            'imageUrl': reverse('catalog:fragrance_image', kwargs={'pk': item.fragrance.pk}) if item.fragrance.source_image_url else None,
            'detailUrl': reverse('catalog:fragrance_detail', kwargs={'pk': item.fragrance.pk}),
            'removeUrl': reverse('accounts:remove_from_wardrobe', kwargs={'item_id': item.id}),
            'shelf': item.shelf,
            'rating': item.personal_rating,
        }
        for item in queryset
    ]
    
    # Diary logs for the tabs:
    diary_logs = (
        ScentLog.objects.filter(user=user)
        .select_related('fragrance', 'fragrance__house')
        .order_by('-wear_date', '-created_at')[:20]
    )
    
    # Lists: group the user's wardrobe items by shelf choice
    shelves_data = {
        'Owned': [],
        'Wishlist': [],
        'Tried': [],
        'Want to Try': [],
    }
    for item in queryset:
        if item.shelf in shelves_data:
            shelves_data[item.shelf].append(item)
        else:
            shelves_data.setdefault(item.shelf, []).append(item)
            
    # Followers and Following counts
    follower_count = user.followers.count()
    following_count = user.following.count()
    
    context = {
        'profile_user': user,
        'profile': profile_obj,
        'is_own_profile': (request.user == user),
        'is_following': is_following,
        'wardrobe_count': wardrobe_count,
        'shelf_items': shelf_items,
        'diary_logs': diary_logs,
        'shelves_data': shelves_data,
        'follower_count': follower_count,
        'following_count': following_count,
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
            'id': item.id,
            'name': item.fragrance.name,
            'house': item.fragrance.house.name,
            'imageUrl': reverse('catalog:fragrance_image', kwargs={'pk': item.fragrance.pk}) if item.fragrance.source_image_url else None,
            'detailUrl': reverse('catalog:fragrance_detail', kwargs={'pk': item.fragrance.pk}),
            'removeUrl': reverse('accounts:remove_from_wardrobe', kwargs={'item_id': item.id}),
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


@login_required
def toggle_follow(request, username):
    """Toggle following status for a user."""
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect('accounts:profile')
        
    follow_rel = Follow.objects.filter(follower=request.user, following=target_user)
    if follow_rel.exists():
        follow_rel.delete()
        messages.success(request, f"You have unfollowed @{target_user.username}.")
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        messages.success(request, f"You are now following @{target_user.username}.")
        
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('accounts:profile', kwargs={'username': username})
    return redirect(next_url)


@login_required
def followers_list(request, username):
    """List followers of a user."""
    target_user = get_object_or_404(User, username=username)
    followers = target_user.followers.select_related('follower', 'follower__profile')
    
    my_following = set(request.user.following.values_list('following_id', flat=True))
    
    items = []
    for f in followers:
        p, _ = Profile.objects.get_or_create(user=f.follower)
        items.append({
            'user': f.follower,
            'profile': p,
            'is_following': f.follower.id in my_following,
            'is_me': f.follower == request.user,
        })
        
    context = {
        'target_user': target_user,
        'network_type': 'followers',
        'items': items,
    }
    return render(request, 'accounts/network.html', context)


@login_required
def following_list(request, username):
    """List users followed by a user."""
    target_user = get_object_or_404(User, username=username)
    following = target_user.following.select_related('following', 'following__profile')
    
    my_following = set(request.user.following.values_list('following_id', flat=True))
    
    items = []
    for f in following:
        p, _ = Profile.objects.get_or_create(user=f.following)
        items.append({
            'user': f.following,
            'profile': p,
            'is_following': f.following.id in my_following,
            'is_me': f.following == request.user,
        })
        
    context = {
        'target_user': target_user,
        'network_type': 'following',
        'items': items,
    }
    return render(request, 'accounts/network.html', context)


@login_required
def feed(request):
    """Display activity feed of followed users and discovery/search options."""
    query = request.GET.get('q', '').strip()
    
    # 1. Handle Member Search
    search_results = []
    if query:
        users = (
            User.objects.filter(
                Q(username__icontains=query) | 
                Q(profile__display_name__icontains=query)
            )
            .exclude(id=request.user.id)
            .select_related('profile')
            .distinct()[:20]
        )
        
        my_following = set(request.user.following.values_list('following_id', flat=True))
        results_data = []
        for u in users:
            p, _ = Profile.objects.get_or_create(user=u)
            results_data.append({
                'user': u,
                'profile': p,
                'is_following': u.id in my_following,
            })
        search_results = results_data

    # 2. Get Followed Users' Activities
    following_ids = list(request.user.following.values_list('following_id', flat=True))
    
    feed_items = []
    if following_ids:
        # Fetch wardrobe additions
        wardrobe_items = (
            WardrobeItem.objects.filter(user_id__in=following_ids)
            .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
            .order_by('-added_at')[:30]
        )
        for item in wardrobe_items:
            feed_items.append({
                'type': 'wardrobe',
                'user': item.user,
                'profile': item.user.profile,
                'fragrance': item.fragrance,
                'shelf': item.shelf,
                'timestamp': item.added_at,
                'id': f"wardrobe_{item.id}"
            })
            
        # Fetch wear diary logs
        scent_logs = (
            ScentLog.objects.filter(user_id__in=following_ids)
            .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
            .order_by('-created_at')[:30]
        )
        for log in scent_logs:
            feed_items.append({
                'type': 'wear',
                'user': log.user,
                'profile': log.user.profile,
                'fragrance': log.fragrance,
                'rating': log.rating,
                'occasion': log.occasion,
                'timestamp': log.created_at,
                'id': f"wear_{log.id}"
            })
            
        # Sort and trim combined activities
        feed_items.sort(key=lambda x: x['timestamp'], reverse=True)
        feed_items = feed_items[:30]

    # 3. Discover People Recommendations (Taste affinity and fallback)
    my_fragrance_ids = list(request.user.wardrobe.values_list('fragrance_id', flat=True))
    similar_taste_users = []
    
    if my_fragrance_ids:
        similar_users_qs = (
            User.objects.filter(wardrobe__fragrance_id__in=my_fragrance_ids)
            .exclude(id=request.user.id)
            .exclude(id__in=following_ids)
            .annotate(shared_count=Count('wardrobe__fragrance_id', distinct=True))
            .select_related('profile')
            .order_by('-shared_count')[:5]
        )
        similar_taste_users = list(similar_users_qs)
        
    if len(similar_taste_users) < 5:
        exclude_ids = [request.user.id] + following_ids + [u.id for u in similar_taste_users]
        popular_users = (
            User.objects.exclude(id__in=exclude_ids)
            .annotate(wardrobe_count=Count('wardrobe'))
            .select_related('profile')
            .order_by('-wardrobe_count')[:5 - len(similar_taste_users)]
        )
        similar_taste_users.extend(list(popular_users))

    context = {
        'query': query,
        'search_results': search_results,
        'feed_items': feed_items,
        'discover_users': similar_taste_users,
        'following_count': len(following_ids),
    }
    return render(request, 'accounts/feed.html', context)


