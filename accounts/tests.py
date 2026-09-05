from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from catalog.models import House, Fragrance
from .models import Profile, WardrobeItem, UserSettings


class AccountsModelTests(TestCase):
    """Tests for profile creation and wardrobe shelf tracking."""

    def setUp(self):
        self.user = User.objects.create_user(username='collector', email='collector@example.com', password='password123')
        self.profile, _ = Profile.objects.get_or_create(user=self.user, defaults={'display_name': 'Nose Extraordinaire'})
        self.house = House.objects.create(name='Maison Francis Kurkdjian')
        self.fragrance = Fragrance.objects.create(name='Baccarat Rouge 540', house=self.house, gender='Unisex')
        self.item = WardrobeItem.objects.create(user=self.user, fragrance=self.fragrance, shelf='Owned')

    def test_wardrobe_item_str(self):
        self.assertEqual(str(self.item), 'collector: Baccarat Rouge 540 [Owned]')

    def test_registration_and_instant_activation(self):
        """Test signup creates an active user directly and logs them in."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newcurator',
            'email': 'newcurator@example.com',
            'password1': 'simple123',
            'password2': 'simple123',
            'agree_to_terms': 'on',
        })
        self.assertRedirects(response, reverse('catalog:index'))

        # Check user is created and active immediately
        new_user = User.objects.get(username='newcurator')
        self.assertTrue(new_user.is_active)
        self.assertEqual(int(self.client.session['_auth_user_id']), new_user.pk)

    def test_password_reset_flow(self):
        """Test password reset request form and views."""
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': 'collector@example.com'
        })
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset', mail.outbox[0].subject)

    def test_logout_clears_session(self):
        """Test logout flushes session data completely."""
        self.client.login(username='collector', password='password123')
        self.client.session['sample_key'] = 'sample_value'
        self.client.session.save()

        response = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('sample_key', self.client.session)

    def test_simplified_mvp_settings(self):
        """Test settings view updates theme, visibility, and shelf preferences."""
        self.client.login(username='collector', password='password123')
        response = self.client.post(reverse('accounts:settings'), {
            'theme': 'Dark',
            'profile_visibility': 'Private',
            'default_shelf': 'Wishlist',
        })
        self.assertRedirects(response, reverse('accounts:settings'))
        
        settings_obj = UserSettings.objects.get(user=self.user)
        self.assertEqual(settings_obj.theme, 'Dark')
        self.assertEqual(settings_obj.profile_visibility, 'Private')
        self.assertEqual(settings_obj.default_shelf, 'Wishlist')

    def test_google_login_button_rendered(self):
        """Test that Continue with Google button renders on login and register pages."""
        login_res = self.client.get(reverse('accounts:login'))
        self.assertEqual(login_res.status_code, 200)
        self.assertContains(login_res, 'Continue with Google')

        register_res = self.client.get(reverse('accounts:register'))
        self.assertEqual(register_res.status_code, 200)
        self.assertContains(register_res, 'Continue with Google')


class AccountsAPITests(TestCase):
    """Unit tests for accounts REST API endpoints (JWT auth, profile, wardrobe, follow, settings)."""

    def setUp(self):
        self.user = User.objects.create_user(username='curator1', email='curator1@example.com', password='password123')
        self.other_user = User.objects.create_user(username='curator2', email='curator2@example.com', password='password123')
        self.profile, _ = Profile.objects.get_or_create(user=self.user, defaults={'display_name': 'Curator One'})
        self.house = House.objects.create(name='Byredo')
        self.fragrance = Fragrance.objects.create(name='Bal d\'Afrique', house=self.house, gender='Unisex')

    def test_jwt_token_obtain_and_refresh(self):
        # Login
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'curator1',
            'password': 'password123'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)

        # Refresh
        refresh_res = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': data['refresh']
        }, content_type='application/json')
        self.assertEqual(refresh_res.status_code, 200)
        self.assertIn('access', refresh_res.json())

    def test_profile_api(self):
        # View own profile
        self.client.login(username='curator1', password='password123')
        response = self.client.get('/api/v1/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'curator1')

        # Edit profile
        edit_res = self.client.patch('/api/v1/profile/edit/', {
            'bio': 'Updated bio via API',
            'location': 'Stockholm'
        }, content_type='application/json')
        self.assertEqual(edit_res.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio via API')
        self.assertEqual(self.profile.location, 'Stockholm')

    def test_wardrobe_api(self):
        self.client.login(username='curator1', password='password123')

        # Add to wardrobe
        add_res = self.client.post(f'/api/v1/wardrobe/add/{self.fragrance.pk}/', {
            'shelf': 'Owned',
            'personal_rating': 5,
            'bottle_size_ml': 50
        }, content_type='application/json')
        self.assertEqual(add_res.status_code, 201)
        item_id = add_res.json()['item']['id']

        # List wardrobe
        list_res = self.client.get('/api/v1/wardrobe/')
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(list_res.json()['count'], 1)

        # Remove from wardrobe
        del_res = self.client.delete(f'/api/v1/wardrobe/{item_id}/')
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(WardrobeItem.objects.filter(user=self.user).count(), 0)

    def test_follow_toggle_api(self):
        self.client.login(username='curator1', password='password123')

        # Cannot follow self
        res_self = self.client.post('/api/v1/profile/curator1/follow/')
        self.assertEqual(res_self.status_code, 400)

        # Follow curator2
        res_follow = self.client.post('/api/v1/profile/curator2/follow/')
        self.assertEqual(res_follow.status_code, 200)
        self.assertTrue(res_follow.json()['following'])

        # Unfollow curator2
        res_unfollow = self.client.post('/api/v1/profile/curator2/follow/')
        self.assertEqual(res_unfollow.status_code, 200)
        self.assertFalse(res_unfollow.json()['following'])

    def test_settings_api(self):
        self.client.login(username='curator1', password='password123')
        response = self.client.patch('/api/v1/settings/', {
            'theme': 'Dark',
            'profile_visibility': 'Private'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['theme'], 'Dark')
        self.assertEqual(data['profile_visibility'], 'Private')


