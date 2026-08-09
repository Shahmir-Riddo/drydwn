from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.test import Client

from catalog.models import Fragrance
from catalog.views import IMAGE_CACHE_TTL


class Command(BaseCommand):
    help = 'Pre-fetch and cache background-removed images for fragrances so pages never hit the slow cold path.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None, help='Only warm the first N fragrances')
        parser.add_argument('--workers', type=int, default=16, help='Concurrent fetch/process threads')

    def handle(self, *args, **options):
        qs = Fragrance.objects.exclude(source_image_url__isnull=True).exclude(source_image_url='')
        if options['limit']:
            qs = qs[:options['limit']]
        pks = list(qs.values_list('pk', flat=True))

        client = Client()
        done = 0

        def warm(pk):
            if cache.get(f'fragrance_image_{pk}') is not None:
                return pk, True
            resp = client.get(f'/fragrance/{pk}/image/')
            return pk, resp.status_code == 200

        with ThreadPoolExecutor(max_workers=options['workers']) as pool:
            futures = [pool.submit(warm, pk) for pk in pks]
            for future in as_completed(futures):
                pk, ok = future.result()
                done += 1
                if not ok:
                    self.stderr.write(f'  failed: fragrance {pk}')
                if done % 50 == 0:
                    self.stdout.write(f'  {done}/{len(pks)}')

        self.stdout.write(self.style.SUCCESS(f'Warmed {done} fragrance images (cache TTL {IMAGE_CACHE_TTL}s)'))
