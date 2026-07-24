from django.shortcuts import render
from .models import WardrobeItem


def wardrobe_index(request):
    """Render user wardrobe collection grouped by shelf category."""
    shelf_filter = request.GET.get('shelf', '')
    queryset = WardrobeItem.objects.select_related('fragrance', 'fragrance__house').all()
    
    if shelf_filter:
        queryset = queryset.filter(shelf=shelf_filter)

    context = {
        'items': queryset,
        'selected_shelf': shelf_filter,
        'total_count': WardrobeItem.objects.count(),
        'owned_count': WardrobeItem.objects.filter(shelf='Owned').count(),
        'wishlist_count': WardrobeItem.objects.filter(shelf='Wishlist').count(),
        'tried_count': WardrobeItem.objects.filter(shelf='Tried').count(),
        'want_to_try_count': WardrobeItem.objects.filter(shelf='Want to Try').count(),
    }
    return render(request, 'accounts/wardrobe.html', context)

