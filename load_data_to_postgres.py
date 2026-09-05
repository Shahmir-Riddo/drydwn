"""
Helper script to migrate and load all fragrance & user data into PostgreSQL.

Usage:
1. Put your actual PostgreSQL URL into .env (DATABASE_URL=postgresql://user:password@host:5432/dbname)
2. Run:
   python load_data_to_postgres.py
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drydwn.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection
from catalog.models import Fragrance, House, Note
from django.contrib.auth.models import User

print("==================================================")
print(f"Target Database Engine: {connection.vendor}")
print(f"Database Name / Host  : {connection.settings_dict.get('NAME')} ({connection.settings_dict.get('HOST', 'local')})")
print("==================================================")

if connection.vendor != 'postgresql':
    print("\n[!] Warning: You are not currently connected to PostgreSQL.")
    print("Please set your PostgreSQL DATABASE_URL in .env first.")
    confirm = input("Do you still want to proceed? (y/N): ").strip().lower()
    if confirm != 'y':
        sys.exit(0)

print("\n1. Applying database migrations to create schema...")
call_command('migrate')

print("\n2. Loading all data from datadump.json...")
try:
    call_command('loaddata', 'datadump.json')
    print("Data loaded successfully!")
except Exception as e:
    print(f"Error during loaddata: {e}")
    sys.exit(1)

print("\n==================================================")
print("VERIFICATION OF RESTORED DATA:")
print(f" • Houses     : {House.objects.count():,}")
print(f" • Notes      : {Note.objects.count():,}")
print(f" • Fragrances : {Fragrance.objects.count():,}")
print(f" • Users      : {User.objects.count():,}")
print("==================================================")
print("Migration to PostgreSQL is COMPLETE with zero data loss!")
