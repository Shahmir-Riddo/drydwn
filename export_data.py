import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drydwn.settings')

import django
django.setup()

from django.core.management import call_command

output_file = 'datadump.json'
print(f"Exporting database to {output_file} with utf-8 encoding...")

with open(output_file, 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        natural_foreign=True,
        natural_primary=True,
        exclude=['contenttypes', 'auth.permission'],
        indent=2,
        stdout=f,
    )

print("Export completed successfully!")
size_mb = os.path.getsize(output_file) / (1024 * 1024)
print(f"Dumpfile size: {size_mb:.2f} MB")
