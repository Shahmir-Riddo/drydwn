import math
from datetime import datetime, timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User
from .models import WardrobeItem, Profile
from diary.models import ScentLog
from catalog.models import Fragrance, Note


def get_user_olfactory_dna(user):
    """Extract user's wardrobe fragrances, wishlist, favorite houses, and note IDs."""
    if not user.is_authenticated:
        return {
            'fragrance_ids': set(),
            'wishlist_ids': set(),
            'owned_ids': set(),
            'note_ids': set(),
            'house_ids': set(),
        }

    wardrobe_items = list(
        WardrobeItem.objects.filter(user=user)
        .select_related('fragrance')
        .prefetch_related('fragrance__top_notes', 'fragrance__heart_notes', 'fragrance__base_notes')
    )

    fragrance_ids = set()
    wishlist_ids = set()
    owned_ids = set()
    note_ids = set()
    house_ids = set()

    for item in wardrobe_items:
        f = item.fragrance
        fragrance_ids.add(f.id)
        house_ids.add(f.house_id)
        if item.shelf in ('Wishlist', 'Want to Try'):
            wishlist_ids.add(f.id)
        elif item.shelf == 'Owned':
            owned_ids.add(f.id)

        for n in f.top_notes.all():
            note_ids.add(n.id)
        for n in f.heart_notes.all():
            note_ids.add(n.id)
        for n in f.base_notes.all():
            note_ids.add(n.id)

    return {
        'fragrance_ids': fragrance_ids,
        'wishlist_ids': wishlist_ids,
        'owned_ids': owned_ids,
        'note_ids': note_ids,
        'house_ids': house_ids,
    }


def get_personalized_feed(user):
    """
    Generate an intelligent, ranked activity feed combining:
    1. Following network updates (highest priority)
    2. Wishlist alerts (community reviews on fragrances the user wants to try)
    3. Olfactory affinity matches (reviews on scents sharing notes with user's wardrobe)
    4. Top community curator highlights
    """
    if not user.is_authenticated:
        return []

    following_ids = set(user.following.values_list('following_id', flat=True))
    dna = get_user_olfactory_dna(user)
    now = datetime.now(timezone.utc)

    feed_candidates = []
    seen_ids = set()

    # Helper: recency weight (half-life of ~7 days)
    def calc_recency_multiplier(dt):
        if not dt:
            return 0.5
        days_old = max(0, (now - dt).total_seconds() / 86400.0)
        return 1.0 / (1.0 + (days_old * 0.15))

    # 1. Activities from Followed Users
    if following_ids:
        # Followed wardrobe additions
        for item in (
            WardrobeItem.objects.filter(user_id__in=following_ids)
            .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
            .order_by('-added_at')[:30]
        ):
            uid = f"wardrobe_{item.id}"
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            recency = calc_recency_multiplier(item.added_at)
            score = 1000.0 * recency
            feed_candidates.append({
                'type': 'wardrobe',
                'user': item.user,
                'profile': getattr(item.user, 'profile', None),
                'fragrance': item.fragrance,
                'shelf': item.shelf,
                'timestamp': item.added_at,
                'id': uid,
                'badge': 'Following',
                'badge_style': 'bg-navy/10 text-navy border-navy/20',
                'score': score,
            })

        # Followed wear diary logs
        for log in (
            ScentLog.objects.filter(user_id__in=following_ids)
            .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
            .order_by('-created_at')[:30]
        ):
            uid = f"wear_{log.id}"
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            recency = calc_recency_multiplier(log.created_at)
            text_bonus = 150.0 if log.review_text else 0.0
            score = (1000.0 + text_bonus) * recency
            feed_candidates.append({
                'type': 'wear',
                'user': log.user,
                'profile': getattr(log.user, 'profile', None),
                'fragrance': log.fragrance,
                'rating': log.rating,
                'occasion': log.occasion,
                'review_text': log.review_text,
                'timestamp': log.created_at,
                'id': uid,
                'badge': 'Following',
                'badge_style': 'bg-navy/10 text-navy border-navy/20',
                'score': score,
            })

    # 2. Olfactory Affinity & Community Discovery Items
    # Find community reviews and wardrobe additions from other curators
    exclude_users = {user.id} | following_ids
    discovery_logs = (
        ScentLog.objects.exclude(user_id__in=exclude_users)
        .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
        .prefetch_related('fragrance__top_notes', 'fragrance__heart_notes', 'fragrance__base_notes')
        .order_by('-created_at')[:40]
    )

    for log in discovery_logs:
        uid = f"wear_{log.id}"
        if uid in seen_ids:
            continue
        seen_ids.add(uid)

        f = log.fragrance
        recency = calc_recency_multiplier(log.created_at)

        # Check if this fragrance is on user's Wishlist
        if f.id in dna['wishlist_ids']:
            badge = 'On Your Wishlist'
            badge_style = 'bg-accent/10 text-accent border-accent/30'
            base_score = 700.0
        elif f.id in dna['owned_ids']:
            badge = 'In Your Wardrobe'
            badge_style = 'bg-sand/40 text-tuxedo border-sand'
            base_score = 500.0
        else:
            # Check note overlap
            f_notes = set(f.top_notes.values_list('id', flat=True)) | \
                      set(f.heart_notes.values_list('id', flat=True)) | \
                      set(f.base_notes.values_list('id', flat=True))
            shared_notes_cnt = len(f_notes & dna['note_ids'])

            if shared_notes_cnt >= 2:
                badge = 'Matches Your Taste'
                badge_style = 'bg-brass/10 text-brass border-brass/30'
                base_score = 400.0 + (shared_notes_cnt * 30.0)
            elif f.house_id in dna['house_ids']:
                badge = 'Favorite House'
                badge_style = 'bg-sand/30 text-tobacco border-sand/50'
                base_score = 350.0
            else:
                badge = 'Community Curated'
                badge_style = 'bg-linen text-tobacco border-sand/30'
                base_score = 250.0

        text_bonus = 120.0 if log.review_text else 0.0
        rating_bonus = (log.rating or 3) * 20.0
        score = (base_score + text_bonus + rating_bonus) * recency

        feed_candidates.append({
            'type': 'wear',
            'user': log.user,
            'profile': getattr(log.user, 'profile', None),
            'fragrance': log.fragrance,
            'rating': log.rating,
            'occasion': log.occasion,
            'review_text': log.review_text,
            'timestamp': log.created_at,
            'id': uid,
            'badge': badge,
            'badge_style': badge_style,
            'score': score,
        })

    # 3. Community Wardrobe Additions for discovery
    discovery_wardrobe = (
        WardrobeItem.objects.exclude(user_id__in=exclude_users)
        .filter(shelf__in=['Owned', 'Wishlist'])
        .select_related('user', 'user__profile', 'fragrance', 'fragrance__house')
        .order_by('-added_at')[:25]
    )

    for item in discovery_wardrobe:
        uid = f"wardrobe_{item.id}"
        if uid in seen_ids:
            continue
        seen_ids.add(uid)

        recency = calc_recency_multiplier(item.added_at)
        f = item.fragrance

        if f.id in dna['wishlist_ids']:
            badge = 'On Your Wishlist'
            badge_style = 'bg-accent/10 text-accent border-accent/30'
            base_score = 600.0
        elif f.house_id in dna['house_ids']:
            badge = 'Favorite House'
            badge_style = 'bg-sand/30 text-tobacco border-sand/50'
            base_score = 320.0
        else:
            badge = 'Community Addition'
            badge_style = 'bg-linen text-tobacco border-sand/30'
            base_score = 200.0

        score = base_score * recency
        feed_candidates.append({
            'type': 'wardrobe',
            'user': item.user,
            'profile': getattr(item.user, 'profile', None),
            'fragrance': item.fragrance,
            'shelf': item.shelf,
            'timestamp': item.added_at,
            'id': uid,
            'badge': badge,
            'badge_style': badge_style,
            'score': score,
        })

    # Sort all candidates by calculated relevance score
    feed_candidates.sort(key=lambda x: x['score'], reverse=True)
    return feed_candidates[:35]


def get_scent_twin_curators(user, limit=5):
    """
    Calculate Olfactory Affinity / Scent Twin matchmaking:
    - Jaccard note overlap percentage
    - Shared wardrobe bottles
    - Highlight top 3 shared note names
    """
    if not user.is_authenticated:
        return []

    following_ids = set(user.following.values_list('following_id', flat=True))
    dna = get_user_olfactory_dna(user)
    my_notes = dna['note_ids']
    my_fragrances = dna['fragrance_ids']

    other_users = (
        User.objects.exclude(id=user.id)
        .select_related('profile')
        .prefetch_related(
            'wardrobe',
            'wardrobe__fragrance',
            'wardrobe__fragrance__top_notes',
            'wardrobe__fragrance__heart_notes',
            'wardrobe__fragrance__base_notes'
        )
    )

    curators = []

    for other in other_users:
        other_wardrobe = list(other.wardrobe.all())
        other_f_ids = {w.fragrance_id for w in other_wardrobe}
        shared_bottles = len(my_fragrances & other_f_ids)

        other_notes = set()
        for w in other_wardrobe:
            f = w.fragrance
            for n in f.top_notes.all():
                other_notes.add(n.id)
            for n in f.heart_notes.all():
                other_notes.add(n.id)
            for n in f.base_notes.all():
                other_notes.add(n.id)

        shared_notes = my_notes & other_notes
        total_unique_notes = len(my_notes | other_notes)

        if total_unique_notes > 0:
            # Scaled Jaccard similarity
            raw_affinity = (len(shared_notes) / total_unique_notes) * 100.0 * 1.6
            affinity_pct = min(99, max(35 if shared_notes else 20, int(round(raw_affinity))))
        else:
            affinity_pct = 40 if shared_bottles else 25

        # Fetch up to 3 shared note names
        shared_note_names = []
        if shared_notes:
            shared_note_names = list(
                Note.objects.filter(id__in=list(shared_notes)[:3])
                .values_list('name', flat=True)
            )

        curators.append({
            'user': other,
            'profile': getattr(other, 'profile', None),
            'is_following': other.id in following_ids,
            'shared_bottles': shared_bottles,
            'shared_notes_count': len(shared_notes),
            'shared_note_names': shared_note_names,
            'affinity_pct': affinity_pct,
            'wardrobe_count': len(other_wardrobe),
        })

    # Sort curators by highest affinity, then shared bottles, then wardrobe size
    curators.sort(
        key=lambda x: (
            not x['is_following'],  # prioritize non-followed first for discovery
            x['affinity_pct'],
            x['shared_bottles'],
            x['wardrobe_count']
        ),
        reverse=True
    )

    return curators[:limit]
