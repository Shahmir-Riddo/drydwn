from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap, index
from catalog.sitemaps import FragranceSitemap, HouseSitemap, NoteSitemap, StaticViewSitemap

sitemaps = {
    'fragrances': FragranceSitemap,
    'houses': HouseSitemap,
    'notes': NoteSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('loadsrn/', TemplateView.as_view(template_name='loading.html'), name='loading'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('terms/', TemplateView.as_view(template_name='legal/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy'),
    path('sitemap.xml', cache_page(86400)(index), {'sitemaps': sitemaps}),
    path('sitemap-<section>.xml', cache_page(86400)(sitemap), {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('accounts/', include('allauth.urls')),
    # REST API v1
    path('api/v1/', include('catalog.api_urls')),
    path('api/v1/', include('diary.api_urls')),
    path('api/v1/', include('accounts.api_urls')),
    # Server-rendered frontend views
    path('', include('catalog.urls')),
    path('diary/', include('diary.urls')),
    path('user/', include('accounts.urls')),
]
