import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin exists, if not, create one
if not User.objects.filter(username='admin').exists():
    print("Creating superuser 'admin'...")
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created successfully!")
else:
    print("Superuser 'admin' already exists.")