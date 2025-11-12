import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from cinema.models import Profile

# Run: python3 create_admin.py

# Create admin
if not User.objects.filter(username='adminTEST').exists():
    admin = User.objects.create_user(
        username='adminTEST',
        email='admin@example.com',
        password='admin123',
        is_staff=True,
        is_active=True
    )
    Profile.objects.create(user=admin, status='Active', subscribed=True)
    print('✅ Admin user created')
else:
    print('Admin user already exists')
