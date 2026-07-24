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

