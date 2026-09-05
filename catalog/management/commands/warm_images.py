import requests as http_requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from django.core.cache import cache

from catalog.models import Fragrance
from catalog.views import IMAGE_CACHE_TTL, _process_and_cache_image


class Command(BaseCommand):
    help = 'Pre-fetch and cache background-removed images for fragrances so pages never hit the slow cold path.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None, help='Only warm the first N fragrances')
        parser.add_argument('--workers', type=int, default=16, help='Concurrent fetch/process threads')

    def handle(self, *args, **options):
        qs = Fragrance.objects.exclude(source_image_url__isnull=True).exclude(source_image_url='')
        if options['limit']:
            qs = qs[:options['limit']]
        pks_and_urls = list(qs.values_list('pk', 'source_image_url'))

        done = 0
        skipped = 0

        def warm(pk, source_url):
            # Check if both variants are already cached
            full_cached = cache.get(f'fragrance_image_v3_{pk}_full') is not None
            thumb_cached = cache.get(f'fragrance_image_v3_{pk}_thumb') is not None
            if full_cached and thumb_cached:
                return pk, True, True  # pk, success, was_skipped

            try:
                resp = http_requests.get(source_url, timeout=10)
                resp.raise_for_status()
                _process_and_cache_image(resp.content, pk)
                return pk, True, False
            except Exception:
                return pk, False, False

        with ThreadPoolExecutor(max_workers=options['workers']) as pool:
            futures = [pool.submit(warm, pk, url) for pk, url in pks_and_urls]
            for future in as_completed(futures):
                pk, ok, was_skipped = future.result()
                done += 1
                if was_skipped:
                    skipped += 1
                elif not ok:
                    self.stderr.write(f'  failed: fragrance {pk}')
                if done % 50 == 0:
                    self.stdout.write(f'  {done}/{len(pks_and_urls)}')

        self.stdout.write(self.style.SUCCESS(
            f'Warmed {done} fragrance images ({skipped} already cached, '
            f'cache TTL {IMAGE_CACHE_TTL}s)'
        ))
