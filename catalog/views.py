
import io
import requests
from PIL import Image
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.core.cache import cache
from .models import House, Note, Fragrance

PAGE_SIZE = 12
IMAGE_CACHE_TTL = 60 * 60 * 24 * 7  # 1 week



# Core Catalog Views

def index(request):
    """Main catalog showcase highlighting featured fragrance compositions."""
    featured_fragrances = Fragrance.objects.select_related('house').all()[:PAGE_SIZE]
    total_count = Fragrance.objects.count()
    context = {
        'featured_fragrances': featured_fragrances,
        'total_count': total_count,
        'has_more': total_count > PAGE_SIZE,
    }
    return render(request, 'catalog/index.html', context)


def load_more_fragrances(request):
    """Return the next page of fragrance cards for the Load More button."""
    offset = int(request.GET.get('offset', 0))
    fragrances = Fragrance.objects.select_related('house').all()[offset:offset + PAGE_SIZE]
    total_count = Fragrance.objects.count()
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
    pixels = img.getdata()
    new_pixels = [
        (r, g, b, 0) if r > 240 and g > 240 and b > 240 else (r, g, b, a)
        for r, g, b, a in pixels
    ]
    img.putdata(new_pixels)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()


def fragrance_image(request, pk):
    """Serve a fragrance's source image with the white background removed, cached in memory."""
    cache_key = f'fragrance_image_v2_{pk}'
    png_bytes = cache.get(cache_key)

    if png_bytes is None:
        fragrance = get_object_or_404(Fragrance, pk=pk)
        if not fragrance.source_image_url:
            raise Http404('No image for this fragrance')

        response = requests.get(fragrance.source_image_url, timeout=10)
        response.raise_for_status()
        png_bytes = _strip_white_background(response.content)
        cache.set(cache_key, png_bytes, IMAGE_CACHE_TTL)

    resp = HttpResponse(png_bytes, content_type='image/png')
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