
import io
import requests
from PIL import Image, ImageChops
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
from django.db.models import Q, Count, F
from django.template.loader import render_to_string
from django.core.cache import cache
from .models import House, Note, Fragrance

PAGE_SIZE = 12
IMAGE_CACHE_TTL = 60 * 60 * 24 * 7  # 1 week
PERSONALIZATION_CACHE_TTL = 60 * 10  # 10 minutes
TOTAL_COUNT_CACHE_TTL = 60 * 5       # 5 minutes


# Core Catalog Views

def _fast_fragrance_queryset():
    """Fast, non-personalized queryset — minimal columns, no aggregations."""
    return (
        Fragrance.objects
        .select_related('house')
        .only('id', 'name', 'gender', 'release_year', 'source_image_url', 'house__name')
        .order_by('name')
    )


def _cached_total_count():
    """Fragrance count, cached for 5 minutes to avoid a COUNT(*) on every load."""
    count = cache.get('fragrance_total_count')
    if count is None:
        count = Fragrance.objects.count()
        cache.set('fragrance_total_count', count, TOTAL_COUNT_CACHE_TTL)
    return count


def _personalized_order(user_id):
    """Return a cached list of fragrance PKs in personalized order.

    Runs the heavy scoring query once and caches the ranked PK list for 10 min.
    Returns None if the user has no signal (empty wardrobe + no follows).
    """
    cache_key = f'personalized_order_{user_id}'
    pk_list = cache.get(cache_key)
    if pk_list is not None:
        return pk_list  # could be [] meaning "no signal"

    from accounts.models import WardrobeItem, Follow

    my_wardrobe = (
        WardrobeItem.objects.filter(user_id=user_id)
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

    following_ids = list(
        Follow.objects.filter(follower_id=user_id).values_list('following_id', flat=True)
    )

    if not my_house_ids and not my_note_ids and not following_ids:
        cache.set(cache_key, [], PERSONALIZATION_CACHE_TTL)
        return []

    annotations = {}
    score_terms = []

    if my_note_ids:
        annotations['top_match'] = Count('top_notes', filter=Q(top_notes__in=my_note_ids), distinct=True)
        annotations['heart_match'] = Count('heart_notes', filter=Q(heart_notes__in=my_note_ids), distinct=True)
        annotations['base_match'] = Count('base_notes', filter=Q(base_notes__in=my_note_ids), distinct=True)
        score_terms.append((F('top_match') + F('heart_match') + F('base_match')) * 4)

    if my_house_ids:
        annotations['house_match'] = Count('id', filter=Q(house_id__in=my_house_ids), distinct=True)
        score_terms.append(F('house_match') * 12)

    if following_ids:
        annotations['social_count'] = Count(
            'wardrobe_entries', filter=Q(wardrobe_entries__user_id__in=following_ids), distinct=True
        )
        score_terms.append(F('social_count') * 20)

    taste_score_expr = score_terms[0]
    for term in score_terms[1:]:
        taste_score_expr = taste_score_expr + term

    pk_list = list(
        Fragrance.objects
        .annotate(**annotations)
        .annotate(taste_score=taste_score_expr)
        .order_by('-taste_score', 'name')
        .values_list('pk', flat=True)
    )
    cache.set(cache_key, pk_list, PERSONALIZATION_CACHE_TTL)
    return pk_list


def _personalized_fragrance_page(user_id, offset, limit):
    """Return a slice of fragrances in personalized order, cheaply.

    Uses the cached PK list and fetches the actual objects in a single
    fast query with no aggregations.
    """
    pk_list = _personalized_order(user_id)
    if not pk_list:
        return None, False  # no personalization signal

    page_pks = pk_list[offset:offset + limit]
    if not page_pks:
        return [], True

    # Fetch objects in bulk, then reorder to match the scored order
    objs = {
        f.pk: f
        for f in (
            Fragrance.objects
            .select_related('house')
            .only('id', 'name', 'gender', 'release_year', 'source_image_url', 'house__name')
            .filter(pk__in=page_pks)
        )
    }
    ordered = [objs[pk] for pk in page_pks if pk in objs]
    return ordered, True


def index(request):
    """Main catalog showcase highlighting featured fragrance compositions, personalized per viewer."""
    total_count = _cached_total_count()
    personalized = False

    if request.user.is_authenticated:
        page, personalized = _personalized_fragrance_page(request.user.id, 0, PAGE_SIZE)
        if personalized and page is not None:
            featured_fragrances = page
        else:
            featured_fragrances = list(_fast_fragrance_queryset()[:PAGE_SIZE])
    else:
        featured_fragrances = list(_fast_fragrance_queryset()[:PAGE_SIZE])

    context = {
        'featured_fragrances': featured_fragrances,
        'total_count': total_count,
        'has_more': total_count > PAGE_SIZE,
        'personalized': personalized,
    }
    return render(request, 'catalog/index.html', context)


def load_more_fragrances(request):
    """Return the next page of fragrance cards for the Load More button, in the same personalized order as index."""
    offset = int(request.GET.get('offset', 0))
    total_count = _cached_total_count()

    if request.user.is_authenticated:
        page, personalized = _personalized_fragrance_page(request.user.id, offset, PAGE_SIZE)
        if personalized and page is not None:
            fragrances = page
        else:
            fragrances = list(_fast_fragrance_queryset()[offset:offset + PAGE_SIZE])
    else:
        fragrances = list(_fast_fragrance_queryset()[offset:offset + PAGE_SIZE])

    html = render_to_string('catalog/_fragrance_cards.html', {'fragrances': fragrances}, request=request)
    return JsonResponse({'html': html, 'has_more': offset + PAGE_SIZE < total_count})


def fragrance_detail(request, pk):
    """Full breakdown of a fragrance including house and top/heart/base note pyramid."""
    fragrance = get_object_or_404(
        Fragrance.objects.select_related('house').prefetch_related('top_notes', 'heart_notes', 'base_notes'),
        pk=pk
    )
    current_shelf = None
    wardrobe_item_id = None
    if request.user.is_authenticated:
        item = request.user.wardrobe.filter(fragrance=fragrance).first()
        if item:
            current_shelf = item.shelf
            wardrobe_item_id = item.id
            
    context = {
        'fragrance': fragrance,
        'current_shelf': current_shelf,
        'wardrobe_item_id': wardrobe_item_id,
    }
    return render(request, 'catalog/fragrance_detail.html', context)


def _strip_white_background(image_bytes):
    """Turn solid-white pixels transparent and crop to the bottle's real bounding box.

    Source photos vary wildly in how much empty margin surrounds the product, so
    cropping to content is what lets every image consistently touch the bottom of
    its frame — without it, drop shadows positioned at a fixed offset drift out of
    alignment depending on each photo's original padding.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    r, g, b, a = img.split()
    
    # Use native point thresholding (runs in compiled C)
    r_mask = r.point(lambda p: 255 if p > 240 else 0)
    g_mask = g.point(lambda p: 255 if p > 240 else 0)
    b_mask = b.point(lambda p: 255 if p > 240 else 0)
    
    # A pixel is considered background white if all R, G, B channels are > 240
    white_mask = ImageChops.darker(ImageChops.darker(r_mask, g_mask), b_mask)
    not_white_mask = ImageChops.invert(white_mask)
    new_a = ImageChops.darker(a, not_white_mask)
    
    img = Image.merge('RGBA', (r, g, b, new_a))
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # Resize to 300px max — card images don't need to be larger
    max_size = 300
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
    out = io.BytesIO()
    img.save(out, format='WEBP', quality=80)
    return out.getvalue()


def fragrance_image(request, pk):
    """Serve a fragrance's source image with the white background removed, cached on disk."""
    cache_key = f'fragrance_image_v3_{pk}'
    img_bytes = cache.get(cache_key)

    if img_bytes is None:
        fragrance = get_object_or_404(Fragrance.objects.only('id', 'source_image_url'), pk=pk)
        if not fragrance.source_image_url:
            raise Http404('No image for this fragrance')

        response = requests.get(fragrance.source_image_url, timeout=10)
        response.raise_for_status()
        img_bytes = _strip_white_background(response.content)
        cache.set(cache_key, img_bytes, IMAGE_CACHE_TTL)

    resp = HttpResponse(img_bytes, content_type='image/webp')
    resp['Cache-Control'] = f'public, max-age={IMAGE_CACHE_TTL}, immutable'
    return resp


# Fragrance Management Views (Staff Only)





class HouseListView(ListView):
    model = House
    ordering = '-id'
    template_name = 'catalog/house_list.html'
    context_object_name = 'houses'
    paginate_by = 30

    def get_queryset(self):
        return House.objects.annotate(fragrance_count=Count('fragrances'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['total_count'] = House.objects.count()
        return context



class HouseDetailView(DetailView):
    model = House
    template_name = 'catalog/house_detail.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fragrances'] = self.object.fragrances.select_related('house').all()[:20]
        return context




house_list = HouseListView.as_view()
house_detail = HouseDetailView.as_view()


# Olfactory Note Views (Staff Only)

class NoteListView(ListView):
    model = Note
    template_name = 'catalog/note_list.html'
    context_object_name = 'notes'
    paginate_by = 50

    def get_queryset(self):
        queryset = Note.objects.all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class NoteDetailView(DetailView):
    model = Note
    template_name = 'catalog/note_detail.html'
    context_object_name = 'note'




note_list = NoteListView.as_view()
note_detail = NoteDetailView.as_view()


# API Endpoint

def api_search(request):
    """Quick search suggestions by fragrance or house name."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    fragrances = Fragrance.objects.filter(
        Q(name__icontains=q) | Q(house__name__icontains=q)
    ).select_related('house')[:8]

    results = [
        {
            'id': f.id,
            'name': f.name,
            'house': f.house.name,
            'image_url': reverse('catalog:fragrance_image', kwargs={'pk': f.id}) if f.source_image_url else '',
            'url': reverse('catalog:fragrance_detail', kwargs={'pk': f.id}),
        }
        for f in fragrances
    ]

    return JsonResponse({'results': results})