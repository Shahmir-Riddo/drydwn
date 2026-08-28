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

    def test_registration_and_email_verification(self):
        """Test signup creates inactive user, sends email, and verification activates account."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newcurator',
            'email': 'newcurator@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'agree_to_terms': 'on',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_done.html')
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify your DRYDOWN Curator Account', mail.outbox[0].subject)

        # Check user is created but inactive
        new_user = User.objects.get(username='newcurator')
        self.assertFalse(new_user.is_active)

        # Test verification URL
        uid = urlsafe_base64_encode(force_bytes(new_user.pk))
        token = default_token_generator.make_token(new_user)
        verify_url = reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        
        verify_response = self.client.get(verify_url, follow=True)
        self.assertEqual(verify_response.status_code, 200)
        
        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)

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

