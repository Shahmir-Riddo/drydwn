from django.test import TestCase
from django.contrib.auth.models import User
from catalog.models import House, Fragrance
from .models import ScentLog


class DiaryModelTests(TestCase):
    """Tests for user wear logs and interaction."""

    def setUp(self):
        self.user = User.objects.create_user(username='fraghead', password='password123')
        self.house = House.objects.create(name='Creed')
        self.fragrance = Fragrance.objects.create(name='Aventus', house=self.house, gender='Men')
        self.log = ScentLog.objects.create(
            user=self.user,
            fragrance=self.fragrance,
            wear_date='2025-01-01',
            rating=4.5,
            occasion='Special'
        )

    def test_scent_log_str(self):
        self.assertEqual(str(self.log), 'fraghead: Aventus (2025-01-01)')


class ScentLogFormTests(TestCase):
    """Tests for ScentLogForm fragrance filtering."""

    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password123')
        self.house = House.objects.create(name='Creed')
        self.fragrance_in_wardrobe = Fragrance.objects.create(name='Aventus', house=self.house, gender='Men')
        self.fragrance_not_in_wardrobe = Fragrance.objects.create(name='Green Irish Tweed', house=self.house, gender='Men')
        
        # Add first fragrance to wardrobe
        from accounts.models import WardrobeItem
        WardrobeItem.objects.create(user=self.user, fragrance=self.fragrance_in_wardrobe, shelf='Owned')

    def test_form_filters_to_wardrobe_when_user_provided(self):
        from .forms import ScentLogForm
        form = ScentLogForm(user=self.user)
        queryset = form.fields['fragrance'].queryset
        self.assertIn(self.fragrance_in_wardrobe, queryset)
        self.assertNotIn(self.fragrance_not_in_wardrobe, queryset)

    def test_form_includes_initial_fragrance_even_if_not_in_wardrobe(self):
        from .forms import ScentLogForm
        form = ScentLogForm(user=self.user, initial={'fragrance': self.fragrance_not_in_wardrobe})
        queryset = form.fields['fragrance'].queryset
        self.assertIn(self.fragrance_in_wardrobe, queryset)
        self.assertIn(self.fragrance_not_in_wardrobe, queryset)


