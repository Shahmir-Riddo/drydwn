from django.contrib import admin
from .models import ScentLog, Like


@admin.register(ScentLog)
class ScentLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'fragrance', 'wear_date', 'rating', 'occasion', 'is_favorite')
    list_filter = ('occasion', 'is_favorite', 'wear_date')
    search_fields = ('user__username', 'fragrance__name', 'review_text')
    raw_id_fields = ('user', 'fragrance')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'scent_log', 'created_at')
    raw_id_fields = ('user', 'scent_log')

