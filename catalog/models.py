from django.db import models


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

