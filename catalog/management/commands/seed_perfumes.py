import csv
import os
import re
import sys
import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from catalog.models import House, Note, Fragrance


class Command(BaseCommand):
    help = 'Import high-volume perfume CSV dataset into catalog app with batch processing'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the perfumes CSV file (e.g. data/perfumes.csv)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='Batch size for database operations (default: 5000)'
        )

    def open_csv_file(self, filepath):
        """Try opening file with utf-8-sig, utf-8, latin-1, cp1252, cp1251 encodings."""
        if not os.path.exists(filepath):
            raise CommandError(f"CSV file not found at path: {filepath}")

        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'cp1251']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f_test:
                    f_test.read(100000)
                return open(filepath, 'r', encoding=enc, errors='replace'), enc
            except (UnicodeDecodeError, UnicodeError):
                continue

        # Fallback to utf-8 with replace
        return open(filepath, 'r', encoding='utf-8', errors='replace'), 'utf-8 (replace)'

    def clean_str(self, val):
        if val is None:
            return ''
        return str(val).strip()

    def clean_year(self, val):
        cleaned = self.clean_str(val)
        if not cleaned:
            return None
        try:
            year = int(float(cleaned))
            if 1700 <= year <= 2100:
                return year
        except (ValueError, TypeError):
            pass
        return None

    def clean_gender(self, val):
        cleaned = self.clean_str(val).lower()
        if not cleaned:
            return 'Unisex'
        if 'women' in cleaned or 'woman' in cleaned or 'female' in cleaned or 'for women' in cleaned:
            return 'Women'
        if 'men' in cleaned or 'man' in cleaned or 'male' in cleaned or 'for men' in cleaned:
            return 'Men'
        return 'Unisex'

    def parse_notes(self, notes_str):
        cleaned = self.clean_str(notes_str)
        if not cleaned or cleaned == '[]':
            return []
        if cleaned.startswith('[') and cleaned.endswith(']'):
            try:
                import ast
                parsed = ast.literal_eval(cleaned)
                if isinstance(parsed, list):
                    return [str(n).strip() for n in parsed if str(n).strip()]
            except Exception:
                pass
        # Split by comma or semicolon
        delimiters = [',', ';']
        for d in delimiters:
            if d in cleaned:
                return [n.strip(" '\"[]") for n in cleaned.split(d) if n.strip(" '\"[]")]
        cleaned_single = cleaned.strip(" '\"[]")
        return [cleaned_single] if cleaned_single else []

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        batch_size = options['batch_size']

        self.stdout.write(self.style.NOTICE(f"Opening CSV file '{csv_file_path}'..."))
        file_obj, encoding_used = self.open_csv_file(csv_file_path)
        self.stdout.write(self.style.SUCCESS(f"Successfully opened file using encoding: {encoding_used}"))

        # Pre-detect delimiter
        sample_line = file_obj.readline()
        file_obj.seek(0)
        delimiter = ';' if ';' in sample_line and sample_line.count(';') > sample_line.count(',') else ','

        # Pre-count total rows if feasible
        total_rows = 0
        try:
            with open(csv_file_path, 'r', encoding=encoding_used.split()[0], errors='replace') as f_count:
                total_rows = sum(1 for _ in f_count) - 1  # subtract header
        except Exception:
            total_rows = 0

        self.stdout.write(self.style.NOTICE("Initializing in-memory House and Note caches..."))
        house_cache = {h.name.lower(): h for h in House.objects.all()}
        note_cache = {n.name.lower(): n for n in Note.objects.all()}

        reader = csv.DictReader(file_obj, delimiter=delimiter)
        
        batch_rows = []
        total_processed = 0
        start_time = time.time()

        # Through models for bulk M2M insertion
        TopNotesThrough = Fragrance.top_notes.through
        HeartNotesThrough = Fragrance.heart_notes.through
        BaseNotesThrough = Fragrance.base_notes.through

        def process_batch(rows):
            nonlocal house_cache, note_cache

            # Collect unique house and note titles for batch lookup
            batch_house_names = set()
            batch_note_names = set()

            parsed_rows = []
            for raw_row in rows:
                # Normalize field keys
                row = {self.clean_str(k).lower(): self.clean_str(v) for k, v in raw_row.items() if k}

                # Extract slug name and convert to display name: "clean-simply-soap" → "Clean Simply Soap"
                slug_name = row.get('name') or row.get('perfume') or row.get('title') or row.get('fragrance') or 'unnamed-fragrance'
                name = slug_name.replace('-', ' ').title()

                house_name = row.get('house') or row.get('brand') or row.get('company') or 'Unknown House'
                gender_str = row.get('gender') or row.get('sex') or row.get('target')
                year_str = row.get('release_year') or row.get('year') or row.get('launch_year')
                top_str = row.get('top_notes') or row.get('top notes') or row.get('top')
                heart_str = row.get('heart_notes') or row.get('heart notes') or row.get('middle_notes') or row.get('heart') or row.get('middle')
                base_str = row.get('base_notes') or row.get('base notes') or row.get('bottom_notes') or row.get('base')

                # Derive image URL from the numeric Fragrantica ID embedded in the URL
                # e.g. https://www.fragrantica.com/perfume/clean/clean-simply-soap-5899.html → 5899
                fragrantica_url = row.get('url') or row.get('source_url') or ''
                image_url = ''
                if fragrantica_url:
                    id_match = re.search(r'-(\d+)\.html', fragrantica_url)
                    if id_match:
                        perfume_id = id_match.group(1)
                        image_url = f'https://fimgs.net/mdimg/perfume/375x500.{perfume_id}.jpg'

                gender = self.clean_gender(gender_str)
                release_year = self.clean_year(year_str)
                top_notes = self.parse_notes(top_str)
                heart_notes = self.parse_notes(heart_str)
                base_notes = self.parse_notes(base_str)

                batch_house_names.add(house_name)
                for n in top_notes + heart_notes + base_notes:
                    batch_note_names.add(n)

                parsed_rows.append({
                    'name': name,
                    'house_name': house_name,
                    'gender': gender,
                    'release_year': release_year,
                    'top_notes': top_notes,
                    'heart_notes': heart_notes,
                    'base_notes': base_notes,
                    'image_url': image_url,
                })

            # Fetch or insert missing houses in bulk and update local cache
            missing_houses = [h for h in batch_house_names if h.lower() not in house_cache]
            if missing_houses:
                new_houses = [House(name=h) for h in missing_houses]
                House.objects.bulk_create(new_houses, ignore_conflicts=True)
                for h in House.objects.filter(name__in=missing_houses):
                    house_cache[h.name.lower()] = h

            # Fetch or insert missing olfactory notes in bulk
            missing_notes = [n for n in batch_note_names if n.lower() not in note_cache]
            if missing_notes:
                new_notes = [Note(name=n) for n in missing_notes]
                Note.objects.bulk_create(new_notes, ignore_conflicts=True)
                for n in Note.objects.filter(name__in=missing_notes):
                    note_cache[n.name.lower()] = n

            # Instantiate fragrance objects and bulk insert
            fragrance_instances = []
            for item in parsed_rows:
                house_obj = house_cache.get(item['house_name'].lower())
                fragrance_instances.append(Fragrance(
                    name=item['name'][:255],
                    house=house_obj,
                    gender=item['gender'],
                    release_year=item['release_year'],
                    source_image_url=item['image_url'][:500] if item['image_url'] else ''
                ))

            with transaction.atomic():
                created_fragrances = Fragrance.objects.bulk_create(fragrance_instances, batch_size=batch_size)

                # Link top, heart, and base notes through many-to-many relationship tables
                top_through_list = []
                heart_through_list = []
                base_through_list = []

                for frag_obj, item in zip(created_fragrances, parsed_rows):
                    for note_name in item['top_notes']:
                        note_obj = note_cache.get(note_name.lower())
                        if note_obj:
                            top_through_list.append(TopNotesThrough(fragrance_id=frag_obj.id, note_id=note_obj.id))

                    for note_name in item['heart_notes']:
                        note_obj = note_cache.get(note_name.lower())
                        if note_obj:
                            heart_through_list.append(HeartNotesThrough(fragrance_id=frag_obj.id, note_id=note_obj.id))

                    for note_name in item['base_notes']:
                        note_obj = note_cache.get(note_name.lower())
                        if note_obj:
                            base_through_list.append(BaseNotesThrough(fragrance_id=frag_obj.id, note_id=note_obj.id))

                if top_through_list:
                    TopNotesThrough.objects.bulk_create(top_through_list, batch_size=batch_size, ignore_conflicts=True)
                if heart_through_list:
                    HeartNotesThrough.objects.bulk_create(heart_through_list, batch_size=batch_size, ignore_conflicts=True)
                if base_through_list:
                    BaseNotesThrough.objects.bulk_create(base_through_list, batch_size=batch_size, ignore_conflicts=True)

        for row in reader:
            batch_rows.append(row)
            if len(batch_rows) >= batch_size:
                process_batch(batch_rows)
                total_processed += len(batch_rows)
                batch_rows = []

                elapsed = time.time() - start_time
                rps = total_processed / elapsed if elapsed > 0 else 0
                if total_rows > 0:
                    pct = (total_processed / total_rows) * 100
                    self.stdout.write(f"Batch completed: {total_processed:,} / {total_rows:,} rows ({pct:.1f}%) [{rps:,.0f} rows/sec]")
                else:
                    self.stdout.write(f"Batch completed: {total_processed:,} rows processed [{rps:,.0f} rows/sec]")

        # Process final remaining rows
        if batch_rows:
            process_batch(batch_rows)
            total_processed += len(batch_rows)

        file_obj.close()
        elapsed_total = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"\nFinished seeding! Successfully processed {total_processed:,} perfume records in {elapsed_total:.2f} seconds."
            )
        )
