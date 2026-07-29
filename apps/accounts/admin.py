"""
Accounts Admin Configuration - EIAMS
=====================================
Registers models with Django Admin and customizes the admin interface
for better management of roles and users.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for Role model."""
    list_display  = ['role_name', 'description', 'created_at']
    search_fields = ['role_name', 'description']
    ordering      = ['role_name']
    list_filter   = ['role_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin extending Django's UserAdmin.
    Displays custom fields (role, full_name, gender, phone, department, status).
    """
    list_display  = [
        'username', 'full_name', 'email', 'get_role_name',
        'department', 'status', 'is_active', 'date_joined'
    ]
    list_filter   = ['role', 'status', 'is_active', 'is_staff', 'gender']
    search_fields = ['username', 'full_name', 'email', 'department']
    ordering      = ['-date_joined']

    # Fields displayed in user detail page
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('full_name', 'email', 'gender', 'phone', 'department', 'profile_pic')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Fields displayed when creating a new user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'full_name', 'email', 'password1', 'password2',
                'role', 'status', 'gender', 'phone', 'department'
            ),
        }),
    )

    def get_role_name(self, obj):
        """Display role name in list view."""
        return obj.get_role_name()
    get_role_name.short_description = 'Role'
