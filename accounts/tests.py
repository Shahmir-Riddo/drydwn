from django.test import TestCase
from django.contrib.auth.models import User
from catalog.models import House, Fragrance
from .models import Profile, WardrobeItem


class AccountsModelTests(TestCase):
    """Tests for profile creation and wardrobe shelf tracking."""

    def setUp(self):
        self.user = User.objects.create_user(username='collector', password='password123')
        self.profile = Profile.objects.create(user=self.user, display_name='Nose Extraordinaire')
        self.house = House.objects.create(name='Maison Francis Kurkdjian')
        self.fragrance = Fragrance.objects.create(name='Baccarat Rouge 540', house=self.house, gender='Unisex')
        self.item = WardrobeItem.objects.create(user=self.user, fragrance=self.fragrance, shelf='Owned')

    def test_wardrobe_item_str(self):
        self.assertEqual(str(self.item), 'collector: Baccarat Rouge 540 [Owned]')

