
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
        print("Superuser 'admin' created with password 'adminpass123'.")
    else:
        # Reset password to ensure we know it
        u = User.objects.get(username='admin')
        u.set_password('adminpass123')
        u.save()
        print("Superuser 'admin' exists. Password reset to 'adminpass123'.")
except Exception as e:
    print(f"Error: {e}")
