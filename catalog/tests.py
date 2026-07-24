from django.test import TestCase
from django.urls import reverse
from .models import House, Note, Fragrance


class CatalogModelTests(TestCase):
    """Tests for fragrance, house, and note catalog models."""

    def setUp(self):
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

