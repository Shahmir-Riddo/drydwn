from django.db import models
from django.contrib.auth.models import User
from catalog.models import Fragrance


class Profile(models.Model):
    """Public user profile and fragrance preference settings."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    favorite_fragrance = models.ForeignKey(
        Fragrance, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='favorited_by_profiles',
        help_text="Signature fragrance preference"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def username(self):
        return self.user.username

    def follower_count(self):
        return self.user.followers.count()

    def following_count(self):
        return self.user.following.count()


class Follow(models.Model):
    """User follow relationship graph."""

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


class WardrobeItem(models.Model):
    """Personal fragrance collection shelf item (e.g. Owned, Wishlist, Tried)."""

    SHELF_CHOICES = [
        ('Owned', 'Owned'),
        ('Wishlist', 'Wishlist'),
        ('Tried', 'Tried'),
        ('Want to Try', 'Want to Try'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wardrobe')
    fragrance = models.ForeignKey(Fragrance, on_delete=models.CASCADE, related_name='wardrobe_entries')
    shelf = models.CharField(max_length=20, choices=SHELF_CHOICES, default='Owned')
    personal_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Rating from 1 to 5"
    )
    bottle_size_ml = models.PositiveIntegerField(default=100, help_text="Bottle size in ML")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'fragrance'], name='unique_wardrobe_entry'),
        ]
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username}: {self.fragrance.name} [{self.shelf}]"

