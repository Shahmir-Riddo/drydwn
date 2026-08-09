from django.db import models
from django.contrib.auth.models import User
from catalog.models import Fragrance
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Profile(models.Model):
    """Public user profile and fragrance preference settings."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
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
    # Modern approach to choices
    class ShelfChoices(models.TextChoices):
        OWNED = 'Owned', 'Owned'
        WISHLIST = 'Wishlist', 'Wishlist'
        TRIED = 'Tried', 'Tried'
        WANT_TO_TRY = 'Want to Try', 'Want to Try'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wardrobe'
    )
    fragrance = models.ForeignKey(
        Fragrance, 
        on_delete=models.CASCADE, 
        related_name='wardrobe_entries'
    )
    shelf = models.CharField(
        max_length=20, 
        choices=ShelfChoices.choices, 
        default=ShelfChoices.OWNED
    )
    personal_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    bottle_size_ml = models.PositiveIntegerField(
        default=100, 
        help_text="Bottle size in ML", 
        null=True, blank=True
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'fragrance'], name='unique_wardrobe_entry'),
        ]
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username}: {self.fragrance.name} [{self.shelf}]"


class UserSettings(models.Model):
    """User preference settings, grouped into 7 main sections."""

    class VisibilityChoices(models.TextChoices):
        PUBLIC = 'Public', 'Public'
        FOLLOWERS_ONLY = 'Followers Only', 'Followers Only'
        PRIVATE = 'Private', 'Private'

    class ThemeChoices(models.TextChoices):
        LIGHT = 'Light', 'Light'
        DARK = 'Dark', 'Dark'
        AUTO = 'Auto', 'Auto'

    class LanguageChoices(models.TextChoices):
        ENGLISH = 'English', 'English'
        ARMENIAN = 'Armenian', 'Armenian'
        RUSSIAN = 'Russian', 'Russian'

    class BottleUnitChoices(models.TextChoices):
        ML = 'ML', 'Milliliters'
        OZ = 'OZ', 'Fluid Ounces'

    class DiaryRetentionChoices(models.TextChoices):
        NEVER = 'Never', 'Never'
        DAYS_90 = '90', '90 Days'
        DAYS_180 = '180', '180 Days'
        DAYS_365 = '365', '365 Days'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')

    # Account
    show_email_on_profile = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    language = models.CharField(max_length=20, choices=LanguageChoices.choices, default=LanguageChoices.ENGLISH)
    remember_me_default = models.BooleanField(default=True)

    # Privacy
    profile_visibility = models.CharField(max_length=20, choices=VisibilityChoices.choices, default=VisibilityChoices.PUBLIC)
    show_wardrobe_publicly = models.BooleanField(default=True)
    show_follower_list = models.BooleanField(default=True)
    allow_follow_requests = models.BooleanField(default=True)

    # Notifications
    email_notifications_enabled = models.BooleanField(default=True)
    notify_new_follower = models.BooleanField(default=True)
    notify_comments_likes = models.BooleanField(default=True)
    weekly_digest_email = models.BooleanField(default=False)

    # Appearance
    theme = models.CharField(max_length=10, choices=ThemeChoices.choices, default=ThemeChoices.AUTO)
    compact_wardrobe_view = models.BooleanField(default=False)
    show_ratings_on_cards = models.BooleanField(default=True)

    # Wardrobe Preferences
    default_shelf = models.CharField(max_length=20, choices=WardrobeItem.ShelfChoices.choices, default=WardrobeItem.ShelfChoices.OWNED)
    bottle_size_unit = models.CharField(max_length=5, choices=BottleUnitChoices.choices, default=BottleUnitChoices.ML)
    auto_add_viewed_to_wishlist = models.BooleanField(default=False)
    show_wardrobe_value_estimate = models.BooleanField(default=False)

    # Social
    allow_tagging = models.BooleanField(default=True)
    show_activity_on_profile = models.BooleanField(default=True)
    discoverable_in_search = models.BooleanField(default=True)

    # Data & Export
    allow_data_export = models.BooleanField(default=True)
    include_wardrobe_in_export = models.BooleanField(default=True)
    diary_retention = models.CharField(max_length=10, choices=DiaryRetentionChoices.choices, default=DiaryRetentionChoices.NEVER)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} settings"