from rest_framework import serializers
from django.urls import reverse
from .models import Note, House, Fragrance, FragranceVote, FragranceRequest


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'name']


class HouseListSerializer(serializers.ModelSerializer):
    fragrance_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = House
        fields = ['id', 'name', 'fragrance_count']


class FragranceMinimalSerializer(serializers.ModelSerializer):
    """Slim fragrance representation for nesting inside house detail."""
    house_name = serializers.CharField(source='house.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Fragrance
        fields = ['id', 'name', 'house_name', 'gender', 'release_year', 'image_url', 'thumbnail_url']

    def get_image_url(self, obj):
        if obj.source_image_url:
            request = self.context.get('request')
            url = reverse('catalog:fragrance_image', kwargs={'pk': obj.pk})
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_thumbnail_url(self, obj):
        if obj.source_image_url:
            request = self.context.get('request')
            url = reverse('catalog:fragrance_image', kwargs={'pk': obj.pk}) + '?size=thumb'
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class HouseDetailSerializer(serializers.ModelSerializer):
    fragrances = serializers.SerializerMethodField()

    class Meta:
        model = House
        fields = ['id', 'name', 'created_at', 'fragrances']

    def get_fragrances(self, obj):
        qs = obj.fragrances.select_related('house').all()[:60]
        return FragranceMinimalSerializer(qs, many=True, context=self.context).data


class FragranceListSerializer(serializers.ModelSerializer):
    house = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Fragrance
        fields = ['id', 'name', 'house', 'gender', 'release_year', 'image_url', 'thumbnail_url']

    def get_house(self, obj):
        return {'id': obj.house_id, 'name': obj.house.name}

    def get_image_url(self, obj):
        if obj.source_image_url:
            request = self.context.get('request')
            url = reverse('catalog:fragrance_image', kwargs={'pk': obj.pk})
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_thumbnail_url(self, obj):
        if obj.source_image_url:
            request = self.context.get('request')
            url = reverse('catalog:fragrance_image', kwargs={'pk': obj.pk}) + '?size=thumb'
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class CommunityInsightOptionSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
    is_user_choice = serializers.BooleanField()


class CommunityInsightCategorySerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    total_votes = serializers.IntegerField()
    options = CommunityInsightOptionSerializer(many=True)
    user_choice = serializers.CharField(allow_null=True)


class ReviewsSummarySerializer(serializers.Serializer):
    avg_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    total_ratings_count = serializers.IntegerField()
    star_breakdown = serializers.ListField()


class ReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='log.id')
    user_name = serializers.CharField()
    username = serializers.CharField(source='user.username')
    avatar_url = serializers.CharField(allow_blank=True)
    initials = serializers.CharField()
    rating = serializers.DecimalField(source='log.rating', max_digits=2, decimal_places=1, allow_null=True)
    wear_date = serializers.DateField(source='log.wear_date')
    occasion = serializers.CharField(source='log.occasion')
    review_text = serializers.CharField(source='log.review_text', allow_blank=True)
    review_title = serializers.CharField()
    descriptor_tags = serializers.ListField(child=serializers.CharField())
    like_count = serializers.IntegerField()
    is_liked_by_user = serializers.BooleanField()
    is_author = serializers.BooleanField()
    is_favorite = serializers.BooleanField(source='log.is_favorite')
    sprays = serializers.IntegerField(source='log.sprays')
    sillage_rating = serializers.IntegerField(source='log.sillage_rating', allow_null=True)
    longevity_hours = serializers.IntegerField(source='log.longevity_hours', allow_null=True)
    created_at = serializers.DateTimeField(source='log.created_at')


class FragranceDetailSerializer(serializers.ModelSerializer):
    house = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    top_notes = NoteSerializer(many=True, read_only=True)
    heart_notes = NoteSerializer(many=True, read_only=True)
    base_notes = NoteSerializer(many=True, read_only=True)
    current_shelf = serializers.SerializerMethodField()
    wardrobe_item_id = serializers.SerializerMethodField()
    community_insights = serializers.SerializerMethodField()
    total_voters = serializers.SerializerMethodField()
    reviews_summary = serializers.SerializerMethodField()

    class Meta:
        model = Fragrance
        fields = [
            'id', 'name', 'house', 'gender', 'release_year', 'image_url',
            'top_notes', 'heart_notes', 'base_notes',
            'current_shelf', 'wardrobe_item_id',
            'community_insights', 'total_voters', 'reviews_summary',
        ]

    def get_house(self, obj):
        return {'id': obj.house_id, 'name': obj.house.name}

    def get_image_url(self, obj):
        if obj.source_image_url:
            request = self.context.get('request')
            url = reverse('catalog:fragrance_image', kwargs={'pk': obj.pk})
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_current_shelf(self, obj):
        user = self.context.get('request', None)
        if user:
            user = user.user
        if user and user.is_authenticated:
            item = user.wardrobe.filter(fragrance=obj).first()
            if item:
                return item.shelf
        return None

    def get_wardrobe_item_id(self, obj):
        user = self.context.get('request', None)
        if user:
            user = user.user
        if user and user.is_authenticated:
            item = user.wardrobe.filter(fragrance=obj).first()
            if item:
                return item.id
        return None

    def get_community_insights(self, obj):
        from .views import _get_community_insights
        request = self.context.get('request')
        user = request.user if request else None
        categories, _ = _get_community_insights(obj, user)
        return CommunityInsightCategorySerializer(categories, many=True).data

    def get_total_voters(self, obj):
        from .views import _get_community_insights
        request = self.context.get('request')
        user = request.user if request else None
        _, total_voters = _get_community_insights(obj, user)
        return total_voters

    def get_reviews_summary(self, obj):
        from .views import _get_reviews_summary_and_page
        summary, _, _ = _get_reviews_summary_and_page(obj)
        return ReviewsSummarySerializer(summary).data


class FragranceVoteSerializer(serializers.Serializer):
    category = serializers.CharField()
    choice = serializers.CharField()

    def validate(self, attrs):
        category = attrs.get('category')
        choice = attrs.get('choice')
        if category not in FragranceVote.CATEGORY_OPTIONS_MAP:
            raise serializers.ValidationError({'category': f'Invalid category. Must be one of: {list(FragranceVote.CATEGORY_OPTIONS_MAP.keys())}'})
        valid_options = FragranceVote.CATEGORY_OPTIONS_MAP[category]
        if choice not in valid_options:
            raise serializers.ValidationError({'choice': f'Invalid choice for {category}. Must be one of: {valid_options}'})
        return attrs


class FragranceRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FragranceRequest
        fields = [
            'id', 'username', 'fragrance_name', 'house_name', 'gender',
            'release_year', 'notes_description', 'reference_url',
            'status', 'upvotes', 'created_at',
        ]
        read_only_fields = ['id', 'username', 'status', 'upvotes', 'created_at']
