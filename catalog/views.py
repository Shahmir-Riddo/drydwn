import io
import requests
from PIL import Image, ImageChops
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
from django.db.models import Q, Count, F, Avg
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.cache import cache
from diary.models import ScentLog
from accounts.models import Profile
from .models import House, Note, Fragrance, FragranceVote
from .utils import search_fragrances

PAGE_SIZE = 24
REVIEWS_PAGE_SIZE = 10
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
    """Return a cached list of fragrance PKs in personalized order."""
    cache_key = f'personalized_order_{user_id}'
    pk_list = cache.get(cache_key)
    if pk_list is not None:
        return pk_list

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
    """Return a slice of fragrances in personalized order, cheaply."""
    pk_list = _personalized_order(user_id)
    if not pk_list:
        return None, False

    page_pks = pk_list[offset:offset + limit]
    if not page_pks:
        return [], True

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
    q = request.GET.get('q', '').strip()
    personalized = False

    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_number = 1
    if page_number < 1:
        page_number = 1

    offset = (page_number - 1) * PAGE_SIZE

    if q:
        search_qs = search_fragrances(q)
        total_count = search_qs.count()
        featured_fragrances = list(search_qs[offset:offset + PAGE_SIZE])
    else:
        total_count = _cached_total_count()
        if request.user.is_authenticated:
            page, personalized = _personalized_fragrance_page(request.user.id, offset, PAGE_SIZE)
            if personalized and page is not None:
                featured_fragrances = page
            else:
                featured_fragrances = list(_fast_fragrance_queryset()[offset:offset + PAGE_SIZE])
        else:
            featured_fragrances = list(_fast_fragrance_queryset()[offset:offset + PAGE_SIZE])

    total_pages = max(1, (total_count + PAGE_SIZE - 1) // PAGE_SIZE) if total_count > 0 else 1
    has_next = page_number < total_pages
    has_previous = page_number > 1

    # Generate smart pagination numbers
    page_numbers = []
    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        left = max(1, page_number - 1)
        right = min(total_pages, page_number + 1)
        if left > 2:
            page_numbers.extend([1, '...'])
            page_numbers.extend(range(left, right + 1))
        else:
            page_numbers.extend(range(1, max(left + 2, 4)))
        if right < total_pages - 1:
            page_numbers.extend(['...', total_pages])
        else:
            for p in range(page_numbers[-1] + 1 if page_numbers else 1, total_pages + 1):
                if p not in page_numbers:
                    page_numbers.append(p)

    context = {
        'featured_fragrances': featured_fragrances,
        'total_count': total_count,
        'has_more': has_next,
        'personalized': personalized,
        'page_number': page_number,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_previous': has_previous,
        'next_page_number': page_number + 1,
        'previous_page_number': page_number - 1,
        'page_numbers': page_numbers,
        'q': q,
    }
    return render(request, 'catalog/index.html', context)


def load_more_fragrances(request):
    """Return the next page of fragrance cards for the Load More button and infinite scroll."""
    offset = int(request.GET.get('offset', 0))
    q = request.GET.get('q', '').strip()

    if q:
        search_qs = search_fragrances(q)
        total_count = search_qs.count()
        fragrances = list(search_qs[offset:offset + PAGE_SIZE])
    else:
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
    has_more = (offset + len(fragrances)) < total_count and len(fragrances) > 0
    return JsonResponse({'html': html, 'has_more': has_more, 'count': len(fragrances)})


# Community Insights & Reviews Configuration

CATEGORIES_CONFIG = [
    {
        'key': 'time_of_day',
        'title': 'Best time of day',
        'options': FragranceVote.TIME_OF_DAY_OPTIONS,
    },
    {
        'key': 'season',
        'title': 'Best season to wear',
        'options': FragranceVote.SEASON_OPTIONS,
    },
    {
        'key': 'longevity',
        'title': 'Longevity',
        'options': FragranceVote.LONGEVITY_OPTIONS,
    },
    {
        'key': 'projection',
        'title': 'Projection',
        'options': FragranceVote.PROJECTION_OPTIONS,
    },
]


def _get_community_insights(fragrance, user=None):
    """Calculate vote counts, percentage distributions, and user choices for community insight bars."""
    votes = FragranceVote.objects.filter(fragrance=fragrance)
    user_votes = {}
    if user and user.is_authenticated:
        user_votes = dict(votes.filter(user=user).values_list('category', 'choice'))

    counts_qs = votes.values('category', 'choice').annotate(count=Count('id'))
    counts_map = {(r['category'], r['choice']): r['count'] for r in counts_qs}

    insight_categories = []
    total_voters = votes.values('user').distinct().count()

    for cat in CATEGORIES_CONFIG:
        cat_key = cat['key']
        cat_total = sum(counts_map.get((cat_key, opt), 0) for opt in cat['options'])

        options_data = []
        for opt in cat['options']:
            cnt = counts_map.get((cat_key, opt), 0)
            pct = round((cnt / cat_total * 100), 1) if cat_total > 0 else 0.0
            options_data.append({
                'name': opt,
                'count': cnt,
                'percentage': pct,
                'is_user_choice': (user_votes.get(cat_key) == opt),
            })

        insight_categories.append({
            'key': cat_key,
            'title': cat['title'],
            'total_votes': cat_total,
            'options': options_data,
            'user_choice': user_votes.get(cat_key),
        })

    return insight_categories, total_voters


def _get_reviews_summary_and_page(fragrance, sort_option='recent', page_number=1, user=None):
    """Calculate overall rating summary, 5-star distribution, and paginated review list."""
    scent_logs = ScentLog.objects.filter(fragrance=fragrance).select_related('user', 'user__profile')
    review_logs = scent_logs.filter(Q(rating__isnull=False) | Q(review_text__gt='')).annotate(like_count=Count('likes'))

    total_reviews = review_logs.count()
    ratings_qs = scent_logs.filter(rating__isnull=False)
    total_ratings_count = ratings_qs.count()

    avg_val = ratings_qs.aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(float(avg_val), 1) if avg_val is not None else 0.0

    # 5-star distribution
    star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in ratings_qs.values_list('rating', flat=True):
        val = float(r)
        if val >= 4.5: star_counts[5] += 1
        elif val >= 3.5: star_counts[4] += 1
        elif val >= 2.5: star_counts[3] += 1
        elif val >= 1.5: star_counts[2] += 1
        elif val >= 0.5: star_counts[1] += 1

    star_breakdown = []
    for stars in [5, 4, 3, 2, 1]:
        cnt = star_counts[stars]
        pct = round((cnt / total_ratings_count * 100), 1) if total_ratings_count > 0 else 0.0
        star_breakdown.append({
            'stars': stars,
            'count': cnt,
            'percentage': pct,
        })

    # Sort reviews
    if sort_option == 'highest':
        logs_qs = review_logs.order_by('-rating', '-created_at')
    elif sort_option == 'lowest':
        logs_qs = review_logs.order_by('rating', '-created_at')
    elif sort_option == 'helpful':
        logs_qs = review_logs.order_by('-like_count', '-created_at')
    else:  # recent
        logs_qs = review_logs.order_by('-created_at', '-wear_date')

    paginator = Paginator(logs_qs, REVIEWS_PAGE_SIZE)
    reviews_page = paginator.get_page(page_number)

    # For user likes on this page
    user_liked_log_ids = set()
    if user and user.is_authenticated:
        from diary.models import Like
        user_liked_log_ids = set(Like.objects.filter(user=user, scent_log__in=reviews_page.object_list).values_list('scent_log_id', flat=True))

    processed_reviews = []
    for log in reviews_page:
        profile = getattr(log.user, 'profile', None)
        name = profile.display_name if profile and profile.display_name else log.user.username
        avatar_url = profile.avatar_url if profile and profile.avatar_url else ''
        
        parts = name.strip().split()
        if len(parts) >= 2:
            initials = (parts[0][0] + parts[-1][0]).upper()
        elif parts:
            initials = parts[0][:2].upper()
        else:
            initials = 'U'

        descriptor_tags = []
        if log.sillage_rating:
            if log.sillage_rating >= 4:
                descriptor_tags.append('Strong Projection')
            elif log.sillage_rating == 3:
                descriptor_tags.append('Moderate Projection')
            else:
                descriptor_tags.append('Soft Sillage')

        if log.longevity_hours:
            if log.longevity_hours >= 8:
                descriptor_tags.append('Long Lasting')
            elif log.longevity_hours >= 4:
                descriptor_tags.append('Moderate Wear')
            else:
                descriptor_tags.append('Light Duration')

        if log.occasion:
            descriptor_tags.append(f'{log.occasion} Wear')

        if log.is_favorite:
            descriptor_tags.append('Standout Choice')

        review_title = ""
        if log.review_text:
            first_sentence = log.review_text.split('.')[0].strip()
            review_title = first_sentence[:60] if len(first_sentence) > 5 else "Wear Session Impression"
        else:
            review_title = f"{log.occasion} Wear Log"

        is_author = bool(user and user.is_authenticated and log.user_id == user.id)

        processed_reviews.append({
            'log': log,
            'user': log.user,
            'user_name': name,
            'avatar_url': avatar_url,
            'initials': initials,
            'review_title': review_title,
            'descriptor_tags': descriptor_tags,
            'like_count': getattr(log, 'like_count', 0),
            'is_liked_by_user': log.id in user_liked_log_ids,
            'is_author': is_author,
        })

    summary = {
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'total_ratings_count': total_ratings_count,
        'star_breakdown': star_breakdown,
    }

    return summary, reviews_page, processed_reviews


def fragrance_detail(request, pk):
    """Full breakdown of a fragrance including notes, community experience bars, and reviews."""
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

    insight_categories, total_voters = _get_community_insights(fragrance, request.user)

    sort_option = request.GET.get('sort', 'recent')
    page_number = int(request.GET.get('page', 1))
    reviews_summary, reviews_page, processed_reviews = _get_reviews_summary_and_page(fragrance, sort_option, page_number, user=request.user)

    context = {
        'fragrance': fragrance,
        'current_shelf': current_shelf,
        'wardrobe_item_id': wardrobe_item_id,
        'insight_categories': insight_categories,
        'total_voters': total_voters,
        'reviews_summary': reviews_summary,
        'reviews_page': reviews_page,
        'processed_reviews': processed_reviews,
        'current_sort': sort_option,
    }
    return render(request, 'catalog/fragrance_detail.html', context)


@login_required
def vote_fragrance(request, pk):
    """Record or update user vote for a fragrance category."""
    fragrance = get_object_or_404(Fragrance, pk=pk)
    if request.method == 'POST':
        category = request.POST.get('category')
        choice = request.POST.get('choice')

        if category in FragranceVote.CATEGORY_OPTIONS_MAP:
            valid_options = FragranceVote.CATEGORY_OPTIONS_MAP[category]
            if choice in valid_options:
                FragranceVote.objects.update_or_create(
                    user=request.user,
                    fragrance=fragrance,
                    category=category,
                    defaults={'choice': choice}
                )
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                    categories_data, total_voters = _get_community_insights(fragrance, request.user)
                    html = render_to_string('catalog/_community_insights.html', {
                        'fragrance': fragrance,
                        'insight_categories': categories_data,
                        'total_voters': total_voters,
                        'user': request.user,
                    }, request=request)
                    return JsonResponse({
                        'success': True,
                        'html': html,
                        'categories': categories_data
                    })

    next_url = request.POST.get('next') or reverse('catalog:fragrance_detail', kwargs={'pk': pk})
    return redirect(next_url)


def load_reviews(request, pk):
    """AJAX handler for sorting and paginating fragrance reviews."""
    fragrance = get_object_or_404(Fragrance, pk=pk)
    sort_option = request.GET.get('sort', 'recent')
    page_number = int(request.GET.get('page', 1))

    reviews_summary, reviews_page, processed_reviews = _get_reviews_summary_and_page(fragrance, sort_option, page_number, user=request.user)

    html = render_to_string('catalog/_reviews_list.html', {
        'fragrance': fragrance,
        'reviews_summary': reviews_summary,
        'reviews_page': reviews_page,
        'processed_reviews': processed_reviews,
        'current_sort': sort_option,
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': reviews_page.has_next(),
        'has_previous': reviews_page.has_previous(),
        'page': reviews_page.number,
        'num_pages': reviews_page.paginator.num_pages,
    })


THUMB_SIZE = 120
FULL_SIZE = 300


def _strip_white_background(image_bytes, max_size=FULL_SIZE):
    """Turn solid-white pixels transparent, crop to bounding box, and resize."""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    r, g, b, a = img.split()
    
    r_mask = r.point(lambda p: 255 if p > 240 else 0)
    g_mask = g.point(lambda p: 255 if p > 240 else 0)
    b_mask = b.point(lambda p: 255 if p > 240 else 0)
    
    white_mask = ImageChops.darker(ImageChops.darker(r_mask, g_mask), b_mask)
    not_white_mask = ImageChops.invert(white_mask)
    new_a = ImageChops.darker(a, not_white_mask)
    
    img = Image.merge('RGBA', (r, g, b, new_a))
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
    out = io.BytesIO()
    img.save(out, format='WEBP', quality=80 if max_size > THUMB_SIZE else 72)
    return out.getvalue()


def _process_and_cache_image(source_bytes, pk):
    """Generate both full and thumb variants from raw source bytes and cache them."""
    full_bytes = _strip_white_background(source_bytes, max_size=FULL_SIZE)
    thumb_bytes = _strip_white_background(source_bytes, max_size=THUMB_SIZE)
    cache.set(f'fragrance_image_v3_{pk}_full', full_bytes, IMAGE_CACHE_TTL)
    cache.set(f'fragrance_image_v3_{pk}_thumb', thumb_bytes, IMAGE_CACHE_TTL)
    return full_bytes, thumb_bytes


def fragrance_image(request, pk):
    """Serve a fragrance's source image with the white background removed, cached on disk."""
    variant = 'thumb' if request.GET.get('size') == 'thumb' else 'full'
    cache_key = f'fragrance_image_v3_{pk}_{variant}'
    img_bytes = cache.get(cache_key)

    if img_bytes is None:
        fragrance = get_object_or_404(Fragrance.objects.only('id', 'source_image_url'), pk=pk)
        if not fragrance.source_image_url:
            raise Http404('No image for this fragrance')

        response = requests.get(fragrance.source_image_url, timeout=10)
        response.raise_for_status()
        full_bytes, thumb_bytes = _process_and_cache_image(response.content, pk)
        img_bytes = thumb_bytes if variant == 'thumb' else full_bytes

    resp = HttpResponse(img_bytes, content_type='image/webp')
    resp['Cache-Control'] = f'public, max-age={IMAGE_CACHE_TTL}, immutable'
    return resp


class HouseListView(ListView):
    model = House
    ordering = '-id'
    template_name = 'catalog/house_list.html'
    context_object_name = 'houses'
    paginate_by = 30

    def get_queryset(self):
        queryset = House.objects.annotate(fragrance_count=Count('fragrances'))
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset

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
        context['fragrances'] = self.object.fragrances.select_related('house').all()[:60]
        return context


house_list = HouseListView.as_view()
house_detail = HouseDetailView.as_view()


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


def api_search(request):
    """Quick search suggestions by fragrance or house name with intelligent matching."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    fragrances = search_fragrances(q)[:10]

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


@login_required
def toggle_like_review(request, log_id):
    """Toggle liking a ScentLog review (helpful vote)."""
    if request.method == 'POST':
        from diary.models import ScentLog, Like
        scent_log = get_object_or_404(ScentLog, pk=log_id)
        like_qs = Like.objects.filter(user=request.user, scent_log=scent_log)
        
        if like_qs.exists():
            like_qs.delete()
            liked = False
        else:
            Like.objects.create(user=request.user, scent_log=scent_log)
            liked = True
            
        like_count = scent_log.likes.count()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({
                'success': True,
                'liked': liked,
                'like_count': like_count
            })
            
    # Fallback to redirecting to referer
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or reverse('catalog:index'))


@login_required
def request_fragrance(request):
    """Allow users to request a new fragrance be added to the catalogue."""
    from .forms import FragranceRequestForm
    from .models import FragranceRequest

    if request.method == 'POST':
        form = FragranceRequestForm(request.POST)
        if form.is_valid():
            frag_request = form.save(commit=False)
            frag_request.user = request.user
            frag_request.save()
            from django.contrib import messages
            messages.success(request, f'Your request for "{frag_request.fragrance_name}" has been submitted. We\'ll review it shortly!')
            return redirect('catalog:request_fragrance')
    else:
        form = FragranceRequestForm()

    # Show recent community requests
    recent_requests = FragranceRequest.objects.select_related('user').order_by('-created_at')[:20]
    user_requests = FragranceRequest.objects.filter(user=request.user).order_by('-created_at')[:10]

    context = {
        'form': form,
        'recent_requests': recent_requests,
        'user_requests': user_requests,
    }
    return render(request, 'catalog/request_fragrance.html', context)