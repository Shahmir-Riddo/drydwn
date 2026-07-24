from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Q
from .models import House, Note, Fragrance
from .forms import HouseForm, NoteForm, FragranceForm


class StaffRequiredMixin(UserPassesTestMixin):
    """Ensure catalog modifications are restricted to staff/admins."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


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
    return render(request, 'catalog/fragrance_detail.html', {'fragrance': fragrance})


# Fragrance Management Views (Staff Only)

class FragranceListView(ListView):
    model = Fragrance
    template_name = 'catalog/fragrance_list.html'
    context_object_name = 'fragrances'
    paginate_by = 24

    def get_queryset(self):
        queryset = Fragrance.objects.select_related('house').prefetch_related('top_notes', 'heart_notes', 'base_notes').all()
        q = self.request.GET.get('q')
        house_id = self.request.GET.get('house')
        gender = self.request.GET.get('gender')

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(house__name__icontains=q)
            )
        if house_id:
            queryset = queryset.filter(house_id=house_id)
        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['houses'] = House.objects.all()
        context['q'] = self.request.GET.get('q', '')
        context['selected_gender'] = self.request.GET.get('gender', '')
        context['selected_house'] = self.request.GET.get('house', '')
        return context


class FragranceCreateView(StaffRequiredMixin, CreateView):
    model = Fragrance
    form_class = FragranceForm
    template_name = 'catalog/fragrance_form.html'
    success_url = reverse_lazy('catalog:index')


class FragranceUpdateView(StaffRequiredMixin, UpdateView):
    model = Fragrance
    form_class = FragranceForm
    template_name = 'catalog/fragrance_form.html'

    def get_success_url(self):
        return reverse_lazy('catalog:fragrance_detail', kwargs={'pk': self.object.pk})


class FragranceDeleteView(StaffRequiredMixin, DeleteView):
    model = Fragrance
    template_name = 'catalog/fragrance_confirm_delete.html'
    success_url = reverse_lazy('catalog:index')


fragrance_list = FragranceListView.as_view()
fragrance_create = FragranceCreateView.as_view()
fragrance_update = FragranceUpdateView.as_view()
fragrance_delete = FragranceDeleteView.as_view()


# House Management Views (Staff Only)

class HouseListView(ListView):
    model = House
    template_name = 'catalog/house_list.html'
    context_object_name = 'houses'
    paginate_by = 30

    def get_queryset(self):
        queryset = House.objects.all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class HouseDetailView(DetailView):
    model = House
    template_name = 'catalog/house_detail.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fragrances'] = self.object.fragrances.select_related('house').all()[:20]
        return context


class HouseCreateView(StaffRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    template_name = 'catalog/house_form.html'
    success_url = reverse_lazy('catalog:house_list')


class HouseUpdateView(StaffRequiredMixin, UpdateView):
    model = House
    form_class = HouseForm
    template_name = 'catalog/house_form.html'

    def get_success_url(self):
        return reverse_lazy('catalog:house_detail', kwargs={'pk': self.object.pk})


class HouseDeleteView(StaffRequiredMixin, DeleteView):
    model = House
    template_name = 'catalog/house_confirm_delete.html'
    success_url = reverse_lazy('catalog:house_list')


house_list = HouseListView.as_view()
house_detail = HouseDetailView.as_view()
house_create = HouseCreateView.as_view()
house_update = HouseUpdateView.as_view()
house_delete = HouseDeleteView.as_view()


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


class NoteCreateView(StaffRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'catalog/note_form.html'
    success_url = reverse_lazy('catalog:note_list')


class NoteUpdateView(StaffRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'catalog/note_form.html'
    success_url = reverse_lazy('catalog:note_list')


class NoteDeleteView(StaffRequiredMixin, DeleteView):
    model = Note
    template_name = 'catalog/note_confirm_delete.html'
    success_url = reverse_lazy('catalog:note_list')


note_list = NoteListView.as_view()
note_detail = NoteDetailView.as_view()
note_create = NoteCreateView.as_view()
note_update = NoteUpdateView.as_view()
note_delete = NoteDeleteView.as_view()


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