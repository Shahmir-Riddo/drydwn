from django.db import models
from django.contrib.auth.models import User
from catalog.models import Fragrance


class ScentLog(models.Model):
    """A user's journal entry capturing a specific fragrance wear session."""

    OCCASION_CHOICES = [
        ('Casual', 'Casual'),
        ('Work', 'Work'),
        ('Evening', 'Evening'),
        ('Formal', 'Formal'),
        ('Special', 'Special Occasion'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scent_logs')
    fragrance = models.ForeignKey(
        Fragrance, on_delete=models.CASCADE,
        related_name='scent_logs'
    )
    wear_date = models.DateField()
    rating = models.DecimalField(
        max_digits=2, decimal_places=1,
        null=True, blank=True,
        help_text="Rating from 0.5 to 5.0"
    )
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, default='Casual')
    sprays = models.PositiveIntegerField(default=3)
    sillage_rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Projection score from 1 (Intimate) to 5 (Enormous)"
    )
    longevity_hours = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Duration of skin wear in hours"
    )
    review_text = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False, help_text="Highlight as a standout wear")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-wear_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-wear_date']),
            models.Index(fields=['fragrance', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.fragrance.name} ({self.wear_date})"


class Like(models.Model):
    """User appreciation or bookmark for a fragrance wear entry."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    scent_log = models.ForeignKey(ScentLog, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'scent_log'], name='unique_like'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.scent_log}"

