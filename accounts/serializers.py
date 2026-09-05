from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from catalog.models import Fragrance
from .models import Profile, WardrobeItem, UserSettings, Follow


# ---------- Auth ----------

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=True,
        )
        Profile.objects.get_or_create(user=user)
        return user


# ---------- Profile ----------

class ProfileSerializer(serializers.ModelSerializer):
    """Read-only profile for public display."""
    username = serializers.CharField(source='user.username', read_only=True)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    favorite_fragrance = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'username', 'display_name', 'bio', 'avatar_url', 'location',
            'favorite_fragrance', 'follower_count', 'following_count',
            'is_following', 'created_at',
        ]

    def get_follower_count(self, obj):
        return obj.user.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return Follow.objects.filter(follower=request.user, following=obj.user).exists()
        return False

    def get_favorite_fragrance(self, obj):
        if obj.favorite_fragrance:
            return {
                'id': obj.favorite_fragrance.id,
                'name': obj.favorite_fragrance.name,
                'house': obj.favorite_fragrance.house.name if obj.favorite_fragrance.house else None,
            }
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Writable profile serializer."""
    email = serializers.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'location', 'avatar_url', 'favorite_fragrance', 'email']

    def validate_favorite_fragrance(self, value):
        # Allow any valid fragrance PK (same as existing dynamic queryset approach)
        if value and not Fragrance.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError('Invalid fragrance.')
        return value

    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        profile = super().update(instance, validated_data)

        if email is not None and email != instance.user.email:
            instance.user.email = email
            instance.user.save(update_fields=['email'])

        return profile


# ---------- Settings ----------

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        exclude = ['id', 'user', 'updated_at']


# ---------- Wardrobe ----------

class WardrobeItemSerializer(serializers.ModelSerializer):
    """Read-only wardrobe item with fragrance detail."""
    fragrance_id = serializers.IntegerField(source='fragrance.id', read_only=True)
    fragrance_name = serializers.CharField(source='fragrance.name', read_only=True)
    house_name = serializers.CharField(source='fragrance.house.name', read_only=True)
    has_image = serializers.SerializerMethodField()

    class Meta:
        model = WardrobeItem
        fields = [
            'id', 'fragrance_id', 'fragrance_name', 'house_name',
            'shelf', 'personal_rating', 'bottle_size_ml',
            'has_image', 'added_at',
        ]

    def get_has_image(self, obj):
        return bool(obj.fragrance.source_image_url)


class WardrobeItemWriteSerializer(serializers.Serializer):
    """Write serializer for adding/updating a wardrobe entry."""
    shelf = serializers.ChoiceField(
        choices=WardrobeItem.ShelfChoices.choices,
        default=WardrobeItem.ShelfChoices.OWNED,
    )
    personal_rating = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=5)
    bottle_size_ml = serializers.IntegerField(required=False, allow_null=True)


# ---------- Follow / Social ----------

class FollowUserSerializer(serializers.Serializer):
    """Compact user info for follower/following lists."""
    username = serializers.CharField()
    display_name = serializers.CharField(allow_blank=True)
    avatar_url = serializers.CharField(allow_blank=True)
    bio = serializers.CharField(allow_blank=True)
    is_following = serializers.BooleanField()
    is_me = serializers.BooleanField()


# ---------- Feed ----------

class FeedItemSerializer(serializers.Serializer):
    """Activity feed item — wardrobe addition or wear log."""
    type = serializers.CharField()
    username = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    fragrance_id = serializers.SerializerMethodField()
    fragrance_name = serializers.SerializerMethodField()
    house_name = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField()
    # Type-specific fields
    shelf = serializers.CharField(required=False, allow_null=True)
    rating = serializers.DecimalField(required=False, allow_null=True, max_digits=2, decimal_places=1)
    occasion = serializers.CharField(required=False, allow_null=True)

    def get_username(self, obj):
        return obj['user'].username

    def get_display_name(self, obj):
        profile = obj.get('profile')
        if profile and profile.display_name:
            return profile.display_name
        return obj['user'].username

    def get_avatar_url(self, obj):
        profile = obj.get('profile')
        return profile.avatar_url if profile else ''

    def get_fragrance_id(self, obj):
        return obj['fragrance'].id

    def get_fragrance_name(self, obj):
        return obj['fragrance'].name

    def get_house_name(self, obj):
        return obj['fragrance'].house.name if obj['fragrance'].house else None
