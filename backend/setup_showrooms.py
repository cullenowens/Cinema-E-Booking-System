"""
Setup script for creating showrooms
Run: python3 setup_showrooms.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cinema.models import Showroom

# Create showrooms
showrooms = ['Showroom A', 'Showroom B', 'Showroom C']

print("Creating showrooms...")

for showroom_name in showrooms:
    showroom, created = Showroom.objects.get_or_create(showroom_name=showroom_name)
    if created:
        print(f'✅ Created {showroom_name}')
    else:
        print(f'{showroom_name} already exists')

print(f'\n✅ Setup complete! {Showroom.objects.count()} showrooms available')
print('\nShowrooms:')
for showroom in Showroom.objects.all():
    print(f'  - {showroom.showroom_name} (ID: {showroom.showroom_id})')