import csv
import json

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponse
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from catalog.models import Fragrance
from diary.models import ScentLog
from .models import Profile, WardrobeItem, UserSettings, Follow
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    UserSettingsSerializer,
    WardrobeItemSerializer,
    WardrobeItemWriteSerializer,
    FollowUserSerializer,
    FeedItemSerializer,
)


# ---------- Auth ----------

class RegisterView(APIView):
    """Register a new user directly and return authentication tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'detail': 'Account created successfully.',
                'username': user.username,
            },
            status=status.HTTP_201_CREATED,
        )


# ---------- Profile ----------

class ProfileView(generics.RetrieveAPIView):
    """View own profile."""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.select_related(
            'user', 'favorite_fragrance', 'favorite_fragrance__house'
        ).get_or_create(user=self.request.user)
        return profile


class ProfileDetailView(generics.RetrieveAPIView):
    """View another user's profile by username."""
    serializer_class = ProfileSerializer
    lookup_field = 'username'

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        profile, _ = Profile.objects.select_related(
            'user', 'favorite_fragrance', 'favorite_fragrance__house'
        ).get_or_create(user=user)
        return profile


class ProfileUpdateView(generics.UpdateAPIView):
    """Edit own profile."""
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


# ---------- Settings ----------

class UserSettingsView(generics.RetrieveUpdateAPIView):
    """View and update user preference settings."""
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        settings_obj, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return settings_obj


# ---------- Wardrobe ----------

class WardrobeListView(generics.ListAPIView):
    """List own wardrobe items, paginated."""
    serializer_class = WardrobeItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WardrobeItem.objects.filter(user=self.request.user)
            .select_related('fragrance', 'fragrance__house')
            .order_by('-added_at')
        )


class WardrobeAddView(APIView):
    """Add or update a fragrance in the user's wardrobe."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, fragrance_id):
        fragrance = get_object_or_404(Fragrance, pk=fragrance_id)
        serializer = WardrobeItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shelf = serializer.validated_data.get('shelf', WardrobeItem.ShelfChoices.OWNED)

        defaults = {'shelf': shelf}
        if serializer.validated_data.get('personal_rating') is not None:
            defaults['personal_rating'] = serializer.validated_data['personal_rating']
        if serializer.validated_data.get('bottle_size_ml') is not None:
            defaults['bottle_size_ml'] = serializer.validated_data['bottle_size_ml']

        item, created = WardrobeItem.objects.update_or_create(
            user=request.user,
            fragrance=fragrance,
            defaults=defaults,
        )

        action = 'added' if created else 'updated'
        return Response({
            'detail': f"Fragrance '{fragrance.name}' {action} on your {shelf} shelf.",
            'item': WardrobeItemSerializer(item).data,
            'created': created,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class WardrobeRemoveView(APIView):
    """Remove an item from the user's wardrobe."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        item = get_object_or_404(WardrobeItem, pk=item_id, user=request.user)
        name = item.fragrance.name
        item.delete()
        return Response({'detail': f"Removed '{name}' from your wardrobe."})


# ---------- Follow ----------

class ToggleFollowView(APIView):
    """Toggle follow/unfollow for a user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        if target_user == request.user:
            return Response(
                {'detail': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_rel = Follow.objects.filter(follower=request.user, following=target_user)
        if follow_rel.exists():
            follow_rel.delete()
            return Response({'detail': f'Unfollowed @{username}.', 'following': False})
        else:
            Follow.objects.create(follower=request.user, following=target_user)
            return Response({'detail': f'Now following @{username}.', 'following': True})


class FollowersListView(APIView):
    """List followers of a user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        target_user = get_object_or_404(User, username=username)
        followers = target_user.followers.select_related('follower', 'follower__profile')
        my_following = set(request.user.following.values_list('following_id', flat=True))

        items = []
        for f in followers:
            p, _ = Profile.objects.get_or_create(user=f.follower)
            items.append({
                'username': f.follower.username,
                'display_name': p.display_name or '',
                'avatar_url': p.avatar_url or '',
                'bio': p.bio or '',
                'is_following': f.follower.id in my_following,
                'is_me': f.follower == request.user,
            })

        return Response(FollowUserSerializer(items, many=True).data)


class FollowingListView(APIView):
    """List users followed by a user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        target_user = get_object_or_404(User, username=username)
        following = target_user.following.select_related('following', 'following__profile')
        my_following = set(request.user.following.values_list('following_id', flat=True))

        items = []
        for f in following:
            p, _ = Profile.objects.get_or_create(user=f.following)
            items.append({
                'username': f.following.username,
                'display_name': p.display_name or '',
                'avatar_url': p.avatar_url or '',
                'bio': p.bio or '',
                'is_following': f.following.id in my_following,
                'is_me': f.following == request.user,
            })

        return Response(FollowUserSerializer(items, many=True).data)


# ---------- Feed ----------

class FeedView(APIView):
    """Activity feed of followed users with member search."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()

        # Member search
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
            for u in users:
                p, _ = Profile.objects.get_or_create(user=u)
                search_results.append({
                    'username': u.username,
                    'display_name': p.display_name or '',
                    'avatar_url': p.avatar_url or '',
                    'bio': p.bio or '',
                    'is_following': u.id in my_following,
                    'is_me': False,
                })

        # Feed items from followed users
        following_ids = list(request.user.following.values_list('following_id', flat=True))
        feed_items = []

        if following_ids:
            wardrobe_items = (
                WardrobeItem.objects.filter(user_id__in=following_ids)
                .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
                .order_by('-added_at')[:30]
            )
            for item in wardrobe_items:
                feed_items.append({
                    'type': 'wardrobe',
                    'user': item.user,
                    'profile': getattr(item.user, 'profile', None),
                    'fragrance': item.fragrance,
                    'shelf': item.shelf,
                    'rating': None,
                    'occasion': None,
                    'timestamp': item.added_at,
                })

            scent_logs = (
                ScentLog.objects.filter(user_id__in=following_ids)
                .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
                .order_by('-created_at')[:30]
            )
            for log in scent_logs:
                feed_items.append({
                    'type': 'wear',
                    'user': log.user,
                    'profile': getattr(log.user, 'profile', None),
                    'fragrance': log.fragrance,
                    'shelf': None,
                    'rating': log.rating,
                    'occasion': log.occasion,
                    'timestamp': log.created_at,
                })

            feed_items.sort(key=lambda x: x['timestamp'], reverse=True)
            feed_items = feed_items[:30]

        # Discover people
        my_fragrance_ids = list(request.user.wardrobe.values_list('fragrance_id', flat=True))
        discover_users = []

        if my_fragrance_ids:
            similar_users = (
                User.objects.filter(wardrobe__fragrance_id__in=my_fragrance_ids)
                .exclude(id=request.user.id)
                .exclude(id__in=following_ids)
                .annotate(shared_count=Count('wardrobe__fragrance_id', distinct=True))
                .select_related('profile')
                .order_by('-shared_count')[:5]
            )
            for u in similar_users:
                p, _ = Profile.objects.get_or_create(user=u)
                discover_users.append({
                    'username': u.username,
                    'display_name': p.display_name or '',
                    'avatar_url': p.avatar_url or '',
                    'bio': p.bio or '',
                    'is_following': False,
                    'is_me': False,
                })

        if len(discover_users) < 5:
            exclude_ids = [request.user.id] + following_ids + [d['username'] for d in discover_users]
            # Re-query using username exclusion won't work, use id list
            existing_discover_usernames = {d['username'] for d in discover_users}
            popular_users = (
                User.objects.exclude(id=request.user.id)
                .exclude(id__in=following_ids)
                .exclude(username__in=existing_discover_usernames)
                .annotate(wardrobe_count=Count('wardrobe'))
                .select_related('profile')
                .order_by('-wardrobe_count')[:5 - len(discover_users)]
            )
            for u in popular_users:
                p, _ = Profile.objects.get_or_create(user=u)
                discover_users.append({
                    'username': u.username,
                    'display_name': p.display_name or '',
                    'avatar_url': p.avatar_url or '',
                    'bio': p.bio or '',
                    'is_following': False,
                    'is_me': False,
                })

        return Response({
            'search_results': FollowUserSerializer(search_results, many=True).data if search_results else [],
            'feed': FeedItemSerializer(feed_items, many=True).data,
            'discover_users': FollowUserSerializer(discover_users, many=True).data,
            'following_count': len(following_ids),
        })


# ---------- Data Export ----------

class ExportDataView(APIView):
    """Export user's collection and scent diary as CSV or JSON."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        fmt = (request.query_params.get('format') or settings_obj.export_format or 'CSV').upper()

        wardrobe_items = (
            WardrobeItem.objects.filter(user=request.user)
            .select_related('fragrance', 'fragrance__house')
            .order_by('-added_at')
        )
        scent_logs = (
            ScentLog.objects.filter(user=request.user)
            .select_related('fragrance', 'fragrance__house')
            .order_by('-wear_date', '-created_at')
        )

        if fmt == 'JSON':
            data = {
                'user': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'display_name': getattr(request.user, 'profile', None) and request.user.profile.display_name,
                },
                'wardrobe': [
                    {
                        'fragrance': item.fragrance.name,
                        'house': item.fragrance.house.name,
                        'shelf': item.shelf,
                        'rating': item.personal_rating,
                        'bottle_size_ml': item.bottle_size_ml,
                        'added_at': item.added_at.isoformat() if item.added_at else None,
                    }
                    for item in wardrobe_items
                ],
                'diary': [
                    {
                        'fragrance': log.fragrance.name if log.fragrance else 'General Wear',
                        'house': log.fragrance.house.name if log.fragrance else None,
                        'wear_date': str(log.wear_date),
                        'rating': float(log.rating) if log.rating else None,
                        'sprays': log.sprays,
                        'occasion': log.occasion,
                        'longevity_hours': log.longevity_hours,
                        'review': log.review_text,
                        'is_favorite': log.is_favorite,
                        'created_at': log.created_at.isoformat() if log.created_at else None,
                    }
                    for log in scent_logs
                ],
            }
            response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="drydown_vault_{request.user.username}.json"'
            return response
        else:
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="drydown_vault_{request.user.username}.csv"'
            writer = csv.writer(response)

            writer.writerow(['--- WARDROBE COLLECTION ---'])
            writer.writerow(['Fragrance', 'House', 'Shelf', 'Rating', 'Bottle Size (ml)', 'Date Added'])
            for item in wardrobe_items:
                writer.writerow([
                    item.fragrance.name,
                    item.fragrance.house.name,
                    item.shelf,
                    item.personal_rating or '',
                    item.bottle_size_ml or '',
                    item.added_at.strftime('%Y-%m-%d %H:%M') if item.added_at else '',
                ])

            writer.writerow([])
            writer.writerow(['--- SCENT DIARY LOGS ---'])
            writer.writerow(['Date', 'Fragrance', 'House', 'Rating', 'Sprays', 'Occasion', 'Longevity (h)', 'Observations', 'Standout'])
            for log in scent_logs:
                writer.writerow([
                    str(log.wear_date),
                    log.fragrance.name if log.fragrance else 'General Wear',
                    log.fragrance.house.name if log.fragrance else '',
                    log.rating or '',
                    log.sprays or '',
                    log.occasion or '',
                    log.longevity_hours or '',
                    log.review_text or '',
                    'Yes' if log.is_favorite else 'No',
                ])

            return response
