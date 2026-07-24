from django.contrib import admin
from .models import Profile, Follow, WardrobeItem


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'location', 'created_at')
    search_fields = ('user__username', 'display_name', 'location')
    raw_id_fields = ('user', 'favorite_fragrance')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    raw_id_fields = ('follower', 'following')


@admin.register(WardrobeItem)
class WardrobeItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'fragrance', 'shelf', 'personal_rating', 'bottle_size_ml', 'added_at')
    list_filter = ('shelf',)
    search_fields = ('user__username', 'fragrance__name')
    raw_id_fields = ('user', 'fragrance')

