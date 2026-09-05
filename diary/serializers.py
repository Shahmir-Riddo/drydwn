from rest_framework import serializers
from .models import ScentLog, Like
from catalog.models import Fragrance


class ScentLogListSerializer(serializers.ModelSerializer):
    """Read-only serializer for diary list view."""
    fragrance_name = serializers.CharField(source='fragrance.name', read_only=True)
    house_name = serializers.CharField(source='fragrance.house.name', read_only=True)
    fragrance_id = serializers.IntegerField(source='fragrance.id', read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = ScentLog
        fields = [
            'id', 'fragrance_id', 'fragrance_name', 'house_name',
            'wear_date', 'rating', 'occasion', 'sprays',
            'sillage_rating', 'longevity_hours', 'is_favorite',
            'like_count', 'created_at',
        ]

    def get_like_count(self, obj):
        return obj.likes.count()


class ScentLogDetailSerializer(serializers.ModelSerializer):
    """Full read-only serializer for diary detail view."""
    fragrance_name = serializers.CharField(source='fragrance.name', read_only=True)
    house_name = serializers.CharField(source='fragrance.house.name', read_only=True)
    fragrance_id = serializers.IntegerField(source='fragrance.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = ScentLog
        fields = [
            'id', 'username', 'fragrance_id', 'fragrance_name', 'house_name',
            'wear_date', 'rating', 'occasion', 'sprays',
            'sillage_rating', 'longevity_hours',
            'review_text', 'is_favorite',
            'like_count', 'created_at',
        ]

    def get_like_count(self, obj):
        return obj.likes.count()


class ScentLogWriteSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating diary entries.

    Preserves the existing form logic: the fragrance must be in the user's
    wardrobe (or be the currently-assigned fragrance when editing).
    """

    class Meta:
        model = ScentLog
        fields = [
            'fragrance', 'wear_date', 'rating', 'occasion',
            'sprays', 'sillage_rating', 'longevity_hours',
            'review_text', 'is_favorite',
        ]

    def validate_fragrance(self, value):
        """Ensure the chosen fragrance is in the user's wardrobe or is the existing one."""
        user = self.context['request'].user
        wardrobe_ids = set(user.wardrobe.values_list('fragrance_id', flat=True))

        # Allow the currently-assigned fragrance when editing
        if self.instance and self.instance.fragrance_id:
            wardrobe_ids.add(self.instance.fragrance_id)

        if value.id not in wardrobe_ids:
            raise serializers.ValidationError(
                'You can only log fragrances that are in your wardrobe.'
            )
        return value
