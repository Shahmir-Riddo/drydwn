from django.contrib import admin
from .models import House, Note, Fragrance


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Fragrance)
class FragranceAdmin(admin.ModelAdmin):
    list_display = ('name', 'house', 'gender', 'release_year')
    list_filter = ('gender', 'release_year')
    search_fields = ('name', 'house__name')
    filter_horizontal = ('top_notes', 'heart_notes', 'base_notes')
    raw_id_fields = ('house',)
    ordering = ('name',)
