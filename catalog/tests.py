from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import House, Note, Fragrance, FragranceVote
from diary.models import ScentLog


class CatalogModelTests(TestCase):
    """Tests for fragrance, house, note models, community votes, and reviews."""

    def setUp(self):
        self.user = User.objects.create_user(username='connoisseur', password='password123')
        self.house = House.objects.create(name='Diptyque')
        self.top_note = Note.objects.create(name='Fig Leaf')
        self.fragrance = Fragrance.objects.create(
            name='Philosykos',
            house=self.house,
            gender='Unisex',
            release_year=1996,
        )
        self.fragrance.top_notes.add(self.top_note)

    def test_fragrance_string_representation(self):
        self.assertEqual(str(self.fragrance), 'Philosykos — Diptyque')

    def test_catalog_index_view(self):
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Philosykos')

    def test_fragrance_detail_view_renders_community_insights(self):
        response = self.client.get(reverse('catalog:fragrance_detail', kwargs={'pk': self.fragrance.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'How Users Experience This Fragrance')
        self.assertContains(response, 'Best time of day')
        self.assertContains(response, 'Longevity')

    def test_fragrance_vote_endpoint(self):
        self.client.login(username='connoisseur', password='password123')
        response = self.client.post(
            reverse('catalog:fragrance_vote', kwargs={'pk': self.fragrance.pk}),
            {'category': 'season', 'choice': 'Fall'}
        )
        self.assertEqual(response.status_code, 302)

        vote = FragranceVote.objects.get(user=self.user, fragrance=self.fragrance, category='season')
        self.assertEqual(vote.choice, 'Fall')

        # Update vote
        self.client.post(
            reverse('catalog:fragrance_vote', kwargs={'pk': self.fragrance.pk}),
            {'category': 'season', 'choice': 'Winter'}
        )
        vote.refresh_from_db()
        self.assertEqual(vote.choice, 'Winter')

    def test_reviews_ajax_endpoint(self):
        response = self.client.get(
            reverse('catalog:fragrance_reviews', kwargs={'pk': self.fragrance.pk}) + '?sort=highest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())

    def test_fragrance_vote_ajax_endpoint(self):
        self.client.login(username='connoisseur', password='password123')
        response = self.client.post(
            reverse('catalog:fragrance_vote', kwargs={'pk': self.fragrance.pk}),
            {'category': 'season', 'choice': 'Spring'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertIn('html', json_data)
        self.assertIn('categories', json_data)

    def test_toggle_like_review_endpoint(self):
        self.client.login(username='connoisseur', password='password123')
        import datetime
        scent_log = ScentLog.objects.create(
            user=self.user,
            fragrance=self.fragrance,
            wear_date=datetime.date.today(),
            rating=5.0,
            review_text="This is an absolute masterpiece."
        )
        
        # Like it
        response = self.client.post(
            reverse('catalog:toggle_like_review', kwargs={'log_id': scent_log.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertTrue(json_data['liked'])
        self.assertEqual(json_data['like_count'], 1)
        
        # Unlike it
        response = self.client.post(
            reverse('catalog:toggle_like_review', kwargs={'log_id': scent_log.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertFalse(json_data['liked'])
        self.assertEqual(json_data['like_count'], 0)

    def test_no_synthetic_seed_data_created_on_detail_view(self):
        """Ensure viewing fragrance detail does NOT create fake seed users or reviews."""
        user_count_before = User.objects.count()
        log_count_before = ScentLog.objects.count()
        vote_count_before = FragranceVote.objects.count()

        response = self.client.get(reverse('catalog:fragrance_detail', kwargs={'pk': self.fragrance.pk}))
        self.assertEqual(response.status_code, 200)

        # Confirm no dummy users or synthetic data injected
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertEqual(ScentLog.objects.count(), log_count_before)
        self.assertEqual(FragranceVote.objects.count(), vote_count_before)
        self.assertContains(response, 'No reviews logged yet')

    def test_load_more_fragrances_endpoint(self):
        """Ensure load more fragrances returns JSON with html and has_more flag."""
        response = self.client.get(reverse('catalog:load_more_fragrances') + '?offset=0')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('html', json_data)
        self.assertIn('has_more', json_data)


