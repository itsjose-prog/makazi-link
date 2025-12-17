import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Try to get the user 'admin', or create it if it doesn't exist
    user, created = User.objects.get_or_create(username='admin')
    
    # FORCE the password reset
    user.set_password('admin123')
    user.email = 'admin@example.com'
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    if created:
        print("--- SUCCESS: Created new superuser 'admin' ---")
    else:
        print("--- SUCCESS: Updated existing superuser 'admin' password to 'admin123' ---")

except Exception as e:
    print(f"--- ERROR: {e} ---")