import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from apps.accounts.models import User

users = User.objects.all().values('id', 'username', 'email', 'is_superuser', 'is_active', 'status')
if users:
    print("=== Existing users ===")
    for u in users:
        print(u)
else:
    print("NO USERS FOUND — you need to create one.")
    print("\nRun: python manage.py createsuperuser")
    print("Or run: python create_admin.py  (see below)")
