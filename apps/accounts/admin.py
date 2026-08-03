"""
Accounts Admin — EIAMS
======================
Enterprise-grade Django Admin registration for the custom User model
and Role model.

Architecture overview
---------------------
* ``UserCreationAdminForm``  — used on the **Add user** page in Django Admin.
  Inherits from ``django.contrib.auth.forms.UserCreationForm`` (the only
  correct base for a ``UserAdmin`` ``add_form``).  Adds all EIAMS-specific
  required fields so the admin can create a complete user record in one step.

* ``UserChangeAdminForm``  — used on the **Change user** page.
  Inherits from ``django.contrib.auth.forms.UserChangeForm`` (the correct
  base for a ``UserAdmin`` ``form``).  Exposes every EIAMS field.

* ``UserModelAdmin``  — registered with ``@admin.register``.
  Sets ``add_form``, ``form``, ``add_fieldsets``, and ``fieldsets``
  so that Django Admin's ``UserAdmin`` machinery works without warnings,
  and the password widget behaves correctly on both add and change pages.

* ``RoleAdmin``  — standard ``ModelAdmin`` for the lookup table.

Compatibility
-------------
* Django 4.x / 5.x / 6.x (``AbstractUser``)
* Python 3.10+ type annotations (``from __future__ import annotations`` is
  *not* used so annotations remain evaluatable at runtime when Django
  inspects them).
"""

from __future__ import annotations

from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Role, User


# ─────────────────────────────────────────────────────────────────────────────
# Forms
# ─────────────────────────────────────────────────────────────────────────────


class UserCreationAdminForm(UserCreationForm):
    """
    Form used exclusively on the Django Admin **Add user** page.

    Extends Django's built-in ``UserCreationForm`` which:
      - provides ``password1`` / ``password2`` with matching + validator logic
      - calls ``user.set_password()`` in ``save()``

    We add every EIAMS-specific field so admins can create a fully-populated
    user record without a second visit to the change page.

    Why *not* a plain ``ModelForm``?
    ---------------------------------
    ``BaseUserAdmin`` explicitly checks ``isinstance(self.add_form, UserCreationForm)``
    to decide whether to invoke ``set_password``.  Using any other base class
    breaks password hashing on creation.
    """

    class Meta(UserCreationForm.Meta):
        # Point at our custom User model; inherit everything else from the
        # parent Meta so field discovery still works correctly.
        model = User
        fields: ClassVar[tuple[str, ...]] = (
            "username",
            "full_name",
            "email",
            "password1",
            "password2",
            "role",
            "gender",
            "phone",
            "department",
            "status",
            "is_staff",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # ``full_name`` is non-nullable on the model, so it must be required.
        self.fields["full_name"].required = True
        # ``email`` carries a ``unique`` constraint on the model; make it
        # required so the admin form rejects missing/duplicate values early.
        self.fields["email"].required = True


class UserChangeAdminForm(UserChangeForm):
    """
    Form used on the Django Admin **Change user** page.

    Extends Django's built-in ``UserChangeForm`` which:
      - renders the password as a read-only hash display with a "change"
        link (the standard Django Admin UX)
      - does *not* expose raw password fields (correct for the change page)

    All EIAMS-specific fields are listed in ``fields`` so the admin
    fieldsets can reference them without raising ``FieldError``.
    """

    class Meta(UserChangeForm.Meta):
        model = User
        fields: ClassVar[str] = "__all__"


# ─────────────────────────────────────────────────────────────────────────────
# User Admin
# ─────────────────────────────────────────────────────────────────────────────


@admin.register(User)
class UserModelAdmin(BaseUserAdmin):
    """
    Django Admin configuration for the custom ``User`` model.

    Key wiring
    ----------
    ``add_form``
        Must be a ``UserCreationForm`` subclass.  Controls the **Add user**
        page.  Django Admin renders ``add_fieldsets`` when this form is active.

    ``form``
        Must be a ``UserChangeForm`` subclass.  Controls the **Change user**
        page.  Django Admin renders ``fieldsets`` when this form is active.

    ``add_fieldsets``
        Sections shown on the **Add user** page.  Every field listed here
        must exist in ``add_form.Meta.fields``.

    ``fieldsets``
        Sections shown on the **Change user** page.  Every field listed
        here must exist on the model (or be provided by ``UserChangeForm``).

    Password behaviour
    ------------------
    * On the **Add user** page ``password1``/``password2`` appear and are
      validated by ``UserCreationForm``, eliminating "This field is required"
      errors.
    * On the **Change user** page the password is shown as a hashed value
      with a "change password" link — exactly as Django intends.
    """

    # ── Form wiring ──────────────────────────────────────────────────────
    add_form = UserCreationAdminForm
    form     = UserChangeAdminForm

    # ── List view ─────────────────────────────────────────────────────────
    list_display: ClassVar[list[str]] = [
        "username",
        "full_name",
        "email",
        "_role_name",
        "department",
        "gender",
        "status",
        "is_active",
        "is_staff",
        "date_joined",
    ]
    list_display_links: ClassVar[list[str]] = ["username", "full_name"]
    list_filter: ClassVar[list[str]] = [
        "role",
        "status",
        "is_active",
        "is_staff",
        "is_superuser",
        "gender",
    ]
    search_fields: ClassVar[list[str]] = [
        "username",
        "full_name",
        "email",
        "department",
        "phone",
    ]
    ordering: ClassVar[list[str]] = ["-date_joined"]
    list_per_page: int = 25
    show_full_result_count: bool = True

    # ── Add-user fieldsets (rendered when add_form is active) ─────────────
    add_fieldsets: ClassVar[tuple] = (
        (
            _("Account Credentials"),
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
                "description": _(
                    "Enter a username and a strong password.  "
                    "The password is validated against the site's password policy."
                ),
            },
        ),
        (
            _("Personal Information"),
            {
                "classes": ("wide",),
                "fields": ("full_name", "email", "gender", "phone"),
            },
        ),
        (
            _("Organisation"),
            {
                "classes": ("wide",),
                "fields": ("department", "role", "status"),
            },
        ),
        (
            _("Permissions"),
            {
                "classes": ("wide", "collapse"),
                "fields": ("is_staff", "is_superuser"),
            },
        ),
    )

    # ── Change-user fieldsets (rendered when form is active) ──────────────
    fieldsets: ClassVar[tuple] = (
        (
            _("Account Credentials"),
            {
                "fields": ("username", "password"),
            },
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    "full_name",
                    "email",
                    "gender",
                    "phone",
                    "profile_pic",
                ),
            },
        ),
        (
            _("Organisation"),
            {
                "fields": ("department", "role", "status"),
            },
        ),
        (
            _("Django Permissions"),
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important Dates"),
            {
                "classes": ("collapse",),
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    # ``last_login`` and ``date_joined`` are auto-managed; make them
    # read-only on the change page so Django does not try to save them.
    readonly_fields: ClassVar[tuple[str, ...]] = ("last_login", "date_joined")

    # ── Custom list-display helpers ───────────────────────────────────────

    @admin.display(description=_("Role"), ordering="role__role_name")
    def _role_name(self, obj: User) -> str:
        """Return the user's role name for the list display column."""
        return obj.get_role_name()


# ─────────────────────────────────────────────────────────────────────────────
# Role Admin
# ─────────────────────────────────────────────────────────────────────────────


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the ``Role`` lookup model.

    Roles are a small, stable set (Super Admin / Admin / Manager / Staff).
    The admin interface is intentionally minimal — roles are managed via
    the seed command in production, not created ad-hoc through the admin.
    """

    list_display: ClassVar[list[str]] = [
        "role_name",
        "description",
        "created_at",
        "updated_at",
    ]
    list_display_links: ClassVar[list[str]] = ["role_name"]
    search_fields: ClassVar[list[str]] = ["role_name", "description"]
    list_filter: ClassVar[list[str]] = ["role_name"]
    ordering: ClassVar[list[str]] = ["role_name"]
    readonly_fields: ClassVar[tuple[str, ...]] = ("created_at", "updated_at")

    fieldsets: ClassVar[tuple] = (
        (
            None,
            {
                "fields": ("role_name", "description"),
            },
        ),
        (
            _("Timestamps"),
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
