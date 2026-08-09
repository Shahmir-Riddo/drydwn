
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q, Count
from .models import House, Note, Fragrance





# Core Catalog Views

def index(request):
    """Main catalog showcase highlighting featured fragrance compositions."""
    featured_fragrances = Fragrance.objects.select_related('house').all()[:12]
    return render(request, 'catalog/index.html', {'featured_fragrances': featured_fragrances})


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
            'image_url': f.source_image_url or '',
            'url': reverse('catalog:fragrance_detail', kwargs={'pk': f.id}),
        }
        for f in fragrances
    ]

    return JsonResponse({'results': results})