"""
Accounts Models - EIAMS
=======================
Defines the data models for user authentication and role management.

Models:
    - Role: Defines user roles (Super Admin, Admin, Manager, Staff)
    - User: Custom user model extending Django's AbstractUser

Tables Created:
    - accounts_role  (corresponds to 'roles' in Data Dictionary)
    - accounts_user  (corresponds to 'users' in Data Dictionary)

Relationships:
    - Role (1) ←→ (∞) User  [One role assigned to many users]
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    Represents a user role in the system.

    Roles define what permissions a user has across the application.
    Four roles are supported: Super Admin, Admin, Manager, Staff.

    Data Dictionary Reference: Table 1 - roles
    """

    # Role name choices - fixed set per requirements
    SUPER_ADMIN = 'Super Admin'
    ADMIN       = 'Admin'
    MANAGER     = 'Manager'
    STAFF       = 'Staff'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (ADMIN,       'Admin'),
        (MANAGER,     'Manager'),
        (STAFF,       'Staff'),
    ]

    # Fields matching Data Dictionary: Table 1 - roles
    role_name   = models.CharField(
        max_length=50,
        unique=True,
        choices=ROLE_CHOICES,
        verbose_name='Role Name',
        help_text='System role: Super Admin / Admin / Manager / Staff'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description',
        help_text='Detailed description of this role and its permissions'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Role'
        verbose_name_plural = 'Roles'
        ordering            = ['role_name']

    def __str__(self):
        return self.role_name

    def is_super_admin(self):
        """Check if this role is Super Admin."""
        return self.role_name == self.SUPER_ADMIN

    def is_admin_or_above(self):
        """Check if this role has Admin-level or higher privileges."""
        return self.role_name in [self.SUPER_ADMIN, self.ADMIN]

    def is_manager_or_above(self):
        """Check if this role has Manager-level or higher privileges."""
        return self.role_name in [self.SUPER_ADMIN, self.ADMIN, self.MANAGER]


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    This model replaces Django's default User with additional fields
    required by the EIAMS system (gender, phone, department, role, status).

    Using AbstractUser allows us to keep all Django auth features
    (login, sessions, permissions) while adding our custom fields.

    Data Dictionary Reference: Table 2 - users
    """

    # Status choices
    STATUS_ACTIVE   = 'Active'
    STATUS_INACTIVE = 'Inactive'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    # Gender choices
    GENDER_MALE   = 'Male'
    GENDER_FEMALE = 'Female'
    GENDER_OTHER  = 'Other'
    GENDER_CHOICES = [
        (GENDER_MALE,   'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER,  'Other'),
    ]

    # ── Fields matching Data Dictionary: Table 2 - users ──────────────────
    role        = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,    # Prevent role deletion if users exist
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Role',
        help_text='Assigned system role for access control'
    )
    full_name   = models.CharField(
        max_length=100,
        verbose_name='Full Name',
        help_text='User\'s full display name'
    )
    gender      = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='Gender'
    )
    phone       = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Phone Number'
    )
    # email is inherited from AbstractUser but we add unique constraint
    email       = models.EmailField(
        unique=True,
        verbose_name='Email Address'
    )
    department  = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Department',
        help_text='Organizational department the user belongs to'
    )
    status      = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Account Status'
    )
    # Profile picture (optional)
    profile_pic = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='Profile Picture'
    )
    # Override username to inherit from AbstractUser (username is unique by default)

    # AbstractUser already provides: username, password, first_name, last_name,
    # email, is_staff, is_active, date_joined, last_login

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.username})"

    def get_role_name(self):
        """Return the user's role name or 'No Role' if unassigned."""
        return self.role.role_name if self.role else 'No Role'

    def is_super_admin(self):
        """Check if user has Super Admin role."""
        return self.role and self.role.role_name == Role.SUPER_ADMIN

    def is_admin_or_above(self):
        """Check if user has Admin or higher privileges."""
        return self.role and self.role.is_admin_or_above()

    def is_manager_or_above(self):
        """Check if user has Manager or higher privileges."""
        return self.role and self.role.is_manager_or_above()

    def is_active_user(self):
        """Check if the user account is active."""
        return self.status == self.STATUS_ACTIVE

    def deactivate(self):
        """Deactivate the user account."""
        self.status = self.STATUS_INACTIVE
        self.is_active = False
        self.save()

    def activate(self):
        """Activate the user account."""
        self.status = self.STATUS_ACTIVE
        self.is_active = True
        self.save()
