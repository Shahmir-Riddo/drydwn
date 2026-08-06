from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Fragrance
from .models import Profile, WardrobeItem
from .forms import SignupForm, EditProfileForm, WardrobeItemForm


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


