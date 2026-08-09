from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Fragrance, House, Note


class FragranceSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Fragrance.objects.only('id').order_by('id')

    def location(self, obj):
        return reverse('catalog:fragrance_detail', kwargs={'pk': obj.pk})


class HouseSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return House.objects.only('id', 'created_at').order_by('id')

    def location(self, obj):
        return reverse('catalog:house_detail', kwargs={'pk': obj.pk})

    def lastmod(self, obj):
        return obj.created_at


class NoteSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.4

    def items(self):
        return Note.objects.only('id').order_by('id')

    def location(self, obj):
        return reverse('catalog:note_detail', kwargs={'pk': obj.pk})


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return ['catalog:index', 'catalog:house_list', 'catalog:note_list', 'terms', 'privacy']

    def location(self, item):
        return reverse(item)
