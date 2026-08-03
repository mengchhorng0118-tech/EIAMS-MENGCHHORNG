"""
Run this once to create the default admin account:
    python create_admin.py

Default credentials:
    Username : admin
    Password : Admin@1234
    Email    : admin@eiams.local
"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from apps.accounts.models import User, Role
from django.db import transaction

USERNAME = 'admin'
PASSWORD = 'Admin@1234'
EMAIL    = 'admin@eiams.local'

with transaction.atomic():
    # Get or create the Super Admin role
    role, _ = Role.objects.get_or_create(
        role_name='Super Admin',
        defaults={'description': 'Full system access'}
    )

    if User.objects.filter(username=USERNAME).exists():
        print(f"User '{USERNAME}' already exists.")
    else:
        user = User.objects.create_superuser(
            username  = USERNAME,
            email     = EMAIL,
            password  = PASSWORD,
            full_name = 'System Administrator',
        )
        user.role   = role
        user.status = User.STATUS_ACTIVE
        user.save()
        print(f"Created superuser '{USERNAME}' successfully.")

print("\n=== All users ===")
for u in User.objects.all().values('username', 'email', 'is_superuser', 'status'):
    print(u)

print(f"\nLogin at: http://127.0.0.1:8000/accounts/login/")
print(f"Username : {USERNAME}")
print(f"Password : {PASSWORD}")
