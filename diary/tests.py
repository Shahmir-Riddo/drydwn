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


class DiaryAPITests(TestCase):
    """Unit tests for diary REST API endpoints (CRUD, permissions, wardrobe filtering)."""

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.house = House.objects.create(name='Tom Ford')
        self.fragrance1 = Fragrance.objects.create(name='Tobacco Vanille', house=self.house, gender='Unisex')
        self.fragrance2 = Fragrance.objects.create(name='Oud Wood', house=self.house, gender='Unisex')

        # Add fragrance1 to user1's wardrobe
        from accounts.models import WardrobeItem
        WardrobeItem.objects.create(user=self.user1, fragrance=self.fragrance1, shelf='Owned')

        # Create scent log for user1
        self.log1 = ScentLog.objects.create(
            user=self.user1,
            fragrance=self.fragrance1,
            wear_date='2026-09-01',
            rating=5.0,
            occasion='Evening',
            sprays=3,
            review_text='Warm and spicy masterpiece.'
        )

    def test_diary_list_api_requires_auth(self):
        response = self.client.get('/api/v1/diary/')
        self.assertEqual(response.status_code, 401)

    def test_diary_list_api_filters_to_authenticated_user(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get('/api/v1/diary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['fragrance_name'], 'Tobacco Vanille')

        # user2 has no logs
        self.client.login(username='user2', password='password123')
        response = self.client.get('/api/v1/diary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)

    def test_diary_create_api_validates_wardrobe(self):
        self.client.login(username='user1', password='password123')

        # fragrance2 is NOT in user1's wardrobe -> should fail validation
        res_fail = self.client.post('/api/v1/diary/', {
            'fragrance': self.fragrance2.id,
            'wear_date': '2026-09-02',
            'rating': 4.0,
            'occasion': 'Work',
            'sprays': 2,
        }, content_type='application/json')
        self.assertEqual(res_fail.status_code, 400)
        self.assertIn('fragrance', res_fail.json())

        # fragrance1 IS in user1's wardrobe -> should succeed
        res_success = self.client.post('/api/v1/diary/', {
            'fragrance': self.fragrance1.id,
            'wear_date': '2026-09-02',
            'rating': 4.5,
            'occasion': 'Work',
            'sprays': 2,
        }, content_type='application/json')
        self.assertEqual(res_success.status_code, 201)

    def test_diary_update_and_delete_permissions(self):
        # user2 cannot edit user1's log
        self.client.login(username='user2', password='password123')
        res_edit_forbidden = self.client.patch(f'/api/v1/diary/{self.log1.pk}/', {
            'rating': 1.0
        }, content_type='application/json')
        self.assertEqual(res_edit_forbidden.status_code, 403)

        # user2 cannot delete user1's log
        res_del_forbidden = self.client.delete(f'/api/v1/diary/{self.log1.pk}/')
        self.assertEqual(res_del_forbidden.status_code, 403)

        # user1 CAN edit own log
        self.client.login(username='user1', password='password123')
        res_edit_ok = self.client.patch(f'/api/v1/diary/{self.log1.pk}/', {
            'rating': 4.0
        }, content_type='application/json')
        self.assertEqual(res_edit_ok.status_code, 200)
        self.log1.refresh_from_db()
        self.assertEqual(float(self.log1.rating), 4.0)

        # user1 CAN delete own log
        res_del_ok = self.client.delete(f'/api/v1/diary/{self.log1.pk}/')
        self.assertEqual(res_del_ok.status_code, 204)
        self.assertFalse(ScentLog.objects.filter(pk=self.log1.pk).exists())



