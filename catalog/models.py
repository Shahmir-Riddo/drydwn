from django.db import models
from django.conf import settings


class House(models.Model):
    """A perfume design house or brand (e.g. Creed, Diptyque)."""

    name = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Note(models.Model):
    """An individual olfactory note element (e.g. Bergamot, Sandalwood, Vetiver)."""

    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Fragrance(models.Model):
    """A fragrance entry with its olfactory pyramid breakdown."""

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='fragrances')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    release_year = models.IntegerField(null=True, blank=True)

    # Fragrance note breakdown (pyramid structure)
    top_notes = models.ManyToManyField(Note, related_name='top_notes', blank=True)
    heart_notes = models.ManyToManyField(Note, related_name='heart_notes', blank=True)
    base_notes = models.ManyToManyField(Note, related_name='base_notes', blank=True)

    source_image_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'house']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.house.name}"


class FragranceVote(models.Model):
    """Community votes on a fragrance across 4 key experience categories."""

    class CategoryChoices(models.TextChoices):
        TIME_OF_DAY = 'time_of_day', 'Best Time of Day'
        SEASON = 'season', 'Best Season'
        LONGEVITY = 'longevity', 'Longevity'
        PROJECTION = 'projection', 'Projection'

    TIME_OF_DAY_OPTIONS = ['Daytime', 'Evening', 'Night out', 'Office']
    SEASON_OPTIONS = ['Spring', 'Summer', 'Fall', 'Winter']
    LONGEVITY_OPTIONS = ['Very weak', 'Weak', 'Moderate', 'Long lasting', 'Eternal']
    PROJECTION_OPTIONS = ['Soft', 'Moderate', 'Strong', 'Enormous']

    CATEGORY_OPTIONS_MAP = {
        'time_of_day': TIME_OF_DAY_OPTIONS,
        'season': SEASON_OPTIONS,
        'longevity': LONGEVITY_OPTIONS,
        'projection': PROJECTION_OPTIONS,
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fragrance_votes')
    fragrance = models.ForeignKey(Fragrance, on_delete=models.CASCADE, related_name='votes')
    category = models.CharField(max_length=20, choices=CategoryChoices.choices)
    choice = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'fragrance', 'category'], name='unique_user_fragrance_category_vote')
        ]
        indexes = [
            models.Index(fields=['fragrance', 'category']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.fragrance.name} [{self.category} -> {self.choice}]"


class FragranceWaft(models.Model):
    """A user's 'Waft' (like / appreciation) for a fragrance in DRYDOWN."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wafts'
    )
    fragrance = models.ForeignKey(
        Fragrance,
        on_delete=models.CASCADE,
        related_name='wafts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'fragrance'], name='unique_user_fragrance_waft')
        ]
        indexes = [
            models.Index(fields=['fragrance', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} wafted {self.fragrance.name}"


class FragranceRequest(models.Model):
    """Community request for a fragrance to be added to the catalogue."""

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        ADDED = 'Added', 'Added'
        DECLINED = 'Declined', 'Declined'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fragrance_requests'
    )
    fragrance_name = models.CharField(max_length=255, blank=True, null=True)
    house_name = models.CharField(max_length=255, blank=True, help_text="Brand or design house name")
    gender = models.CharField(max_length=10, choices=Fragrance.GENDER_CHOICES, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    notes_description = models.TextField(
        blank=True,
        help_text="Any known notes or additional details about the fragrance"
    )
    reference_url = models.URLField(
        max_length=500, blank=True,
        help_text="Link to Fragrantica, Parfumo, or official page"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    admin_note = models.TextField(blank=True, help_text="Internal note from the team")
    upvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        house = f" — {self.house_name}" if self.house_name else ""
        return f"{self.fragrance_name}{house} ({self.status})"

