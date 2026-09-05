from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

from .models import Note, House, Fragrance, FragranceVote, FragranceRequest
from .serializers import (
    NoteSerializer, HouseListSerializer, HouseDetailSerializer,
    FragranceListSerializer, FragranceDetailSerializer,
    FragranceVoteSerializer, FragranceRequestSerializer,
    ReviewSerializer, CommunityInsightCategorySerializer,
)
from .views import (
    _fast_fragrance_queryset, _cached_total_count,
    _personalized_fragrance_page, _get_community_insights,
    _get_reviews_summary_and_page,
)
from diary.models import ScentLog, Like


# ---------- Custom paginators ----------

class HousePagination(PageNumberPagination):
    page_size = 30


class NotePagination(PageNumberPagination):
    page_size = 50


class ReviewPagination(PageNumberPagination):
    page_size = 10


# ---------- Fragrance endpoints ----------

class FragranceListView(generics.ListAPIView):
    """Paginated fragrance catalog with optional search and personalized ordering."""
    serializer_class = FragranceListSerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if q:
            return (
                Fragrance.objects.filter(
                    Q(name__icontains=q) | Q(house__name__icontains=q)
                )
                .select_related('house')
                .only('id', 'name', 'gender', 'release_year', 'source_image_url', 'house__name')
                .order_by('name')
            )
        return _fast_fragrance_queryset()

    def list(self, request, *args, **kwargs):
        q = request.query_params.get('q', '').strip()
        if not q and request.user.is_authenticated:
            try:
                page_number = int(request.query_params.get('page', 1))
            except ValueError:
                page_number = 1

            page_size = self.paginator.get_page_size(request) if self.paginator else 24
            offset = max(0, (page_number - 1) * page_size)
            items, personalized = _personalized_fragrance_page(request.user.id, offset, page_size)

            if personalized and items is not None:
                total_count = _cached_total_count()
                serializer = self.get_serializer(items, many=True)

                base_url = request.build_absolute_uri(request.path)
                has_next = (offset + len(items)) < total_count and len(items) > 0
                has_prev = page_number > 1

                next_link = f"{base_url}?page={page_number + 1}" if has_next else None
                prev_link = f"{base_url}?page={page_number - 1}" if has_prev and page_number > 2 else (base_url if has_prev else None)

                return Response({
                    'count': total_count,
                    'next': next_link,
                    'previous': prev_link,
                    'results': serializer.data,
                })

        return super().list(request, *args, **kwargs)


class FragranceDetailView(generics.RetrieveAPIView):
    """Full fragrance detail with notes, community insights, and reviews summary."""
    serializer_class = FragranceDetailSerializer

    def get_queryset(self):
        return (
            Fragrance.objects.select_related('house')
            .prefetch_related('top_notes', 'heart_notes', 'base_notes')
        )


class FragranceReviewsView(APIView):
    """Paginated reviews for a fragrance with sorting."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        fragrance = get_object_or_404(Fragrance, pk=pk)
        sort_option = request.query_params.get('sort', 'recent')
        page_number = int(request.query_params.get('page', 1))

        reviews_summary, reviews_page, processed_reviews = _get_reviews_summary_and_page(
            fragrance, sort_option, page_number, user=request.user
        )

        reviews_data = ReviewSerializer(processed_reviews, many=True).data

        return Response({
            'summary': reviews_summary,
            'reviews': reviews_data,
            'page': reviews_page.number,
            'num_pages': reviews_page.paginator.num_pages,
            'has_next': reviews_page.has_next(),
            'has_previous': reviews_page.has_previous(),
        })


class FragranceVoteView(APIView):
    """Record or update a community vote on a fragrance category."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        fragrance = get_object_or_404(Fragrance, pk=pk)
        serializer = FragranceVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        FragranceVote.objects.update_or_create(
            user=request.user,
            fragrance=fragrance,
            category=serializer.validated_data['category'],
            defaults={'choice': serializer.validated_data['choice']}
        )

        categories_data, total_voters = _get_community_insights(fragrance, request.user)
        insights = CommunityInsightCategorySerializer(categories_data, many=True).data

        return Response({
            'success': True,
            'insights': insights,
            'total_voters': total_voters,
        })


class FragranceSearchView(APIView):
    """Quick-search autocomplete suggestions by fragrance or house name."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'results': []})

        fragrances = (
            Fragrance.objects.filter(
                Q(name__icontains=q) | Q(house__name__icontains=q)
            )
            .select_related('house')[:8]
        )

        from django.urls import reverse
        results = [
            {
                'id': f.id,
                'name': f.name,
                'house': f.house.name,
                'image_url': (
                    request.build_absolute_uri(reverse('catalog:fragrance_image', kwargs={'pk': f.id}))
                    if f.source_image_url else None
                ),
                'thumbnail_url': (
                    request.build_absolute_uri(reverse('catalog:fragrance_image', kwargs={'pk': f.id}) + '?size=thumb')
                    if f.source_image_url else None
                ),
            }
            for f in fragrances
        ]

        return Response({'results': results})


# ---------- House endpoints ----------

class HouseListView(generics.ListAPIView):
    """Paginated list of perfume houses with fragrance count and optional search."""
    serializer_class = HouseListSerializer
    pagination_class = HousePagination

    def get_queryset(self):
        queryset = House.objects.annotate(fragrance_count=Count('fragrances')).order_by('name')
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class HouseDetailView(generics.RetrieveAPIView):
    """House detail with nested fragrances."""
    serializer_class = HouseDetailSerializer
    queryset = House.objects.all()


# ---------- Note endpoints ----------

class NoteListView(generics.ListAPIView):
    """Paginated list of fragrance notes with optional search."""
    serializer_class = NoteSerializer
    pagination_class = NotePagination

    def get_queryset(self):
        queryset = Note.objects.all()
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class NoteDetailView(generics.RetrieveAPIView):
    """Single note detail."""
    serializer_class = NoteSerializer
    queryset = Note.objects.all()


# ---------- Review Like toggle ----------

class ToggleLikeView(APIView):
    """Toggle a 'helpful' like on a ScentLog review."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, log_id):
        scent_log = get_object_or_404(ScentLog, pk=log_id)
        like_qs = Like.objects.filter(user=request.user, scent_log=scent_log)

        if like_qs.exists():
            like_qs.delete()
            liked = False
        else:
            Like.objects.create(user=request.user, scent_log=scent_log)
            liked = True

        like_count = scent_log.likes.count()
        return Response({
            'success': True,
            'liked': liked,
            'like_count': like_count,
        })


# ---------- Fragrance Request ----------

class FragranceRequestListCreateView(generics.ListCreateAPIView):
    """List community fragrance requests and submit new ones."""
    serializer_class = FragranceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FragranceRequest.objects.select_related('user').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
