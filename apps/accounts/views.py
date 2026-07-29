"""
Accounts Views - EIAMS
======================
Handles all user authentication and user management operations.

Views:
    - login_view          : Authenticate and establish user session
    - logout_view         : Terminate session and redirect to login
    - user_list           : List all users with search and pagination
    - user_create         : Admin creates new user
    - user_update         : Admin updates user details
    - user_delete         : Admin deactivates user (soft delete)
    - user_detail         : View user profile details
    - profile_view        : User views/updates own profile
    - change_password     : User changes own password
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from .models import User, Role
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm,
    ProfileUpdateForm, CustomPasswordChangeForm
)
from .decorators import admin_or_above_required, super_admin_required

# Tab anchors returned on error so the browser opens the right tab
_TAB_ANCHOR = {
    'profile':  '#tabEdit',
    'password': '#tabSecurity',
}


def accounts_home(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('accounts:intro')   # go to intro first, not login directly


def intro_view(request):
    """
    Animated feature slideshow shown before the login page.
    Unauthenticated users only — authenticated users skip to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'accounts/intro.html')


# ──────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ──────────────────────────────────────────────────────────────

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

# ──────────────────────────────────────────────────────────────
# AUTHENTICATION VIEWS
# ──────────────────────────────────────────────────────────────

def login_view(request):
    """
    Handle user login with CSRF protection.

    GET:  Display the login form.
    POST: Validate credentials, establish session, redirect to dashboard.

    Features:
    - Remember Me: Extends session to 30 days if checked
    - Descriptive error messages for invalid credentials
    - Redirects authenticated users directly to dashboard
    """
    # Redirect already authenticated users to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if account is active
                if user.status == User.STATUS_INACTIVE:
                    messages.error(
                        request,
                        'Your account has been deactivated. Please contact the administrator.'
                    )
                    return render(request, 'accounts/login.html', {'form': form})

                # Establish session
                login(request, user)

                # Handle Remember Me: extend session to 30 days
                if remember:
                    request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
                else:
                    request.session.set_expiry(0)  # Session expires on browser close

                messages.success(request, f'Welcome back, {user.full_name}!')

                # Redirect to 'next' parameter or dashboard
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:home')
            else:
                messages.error(
                    request,
                    'Invalid username or password. Please check your credentials and try again.'
                )
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Terminate user session and redirect to login page.
    Only processes POST requests to prevent CSRF logout attacks.
    """
    if request.method == 'POST':
        username = request.user.full_name if request.user.is_authenticated else 'User'
        logout(request)
        messages.success(request, f'You have been logged out successfully. Goodbye, {username}!')
    return redirect('accounts:login')


# ──────────────────────────────────────────────────────────────
# USER MANAGEMENT VIEWS
# ──────────────────────────────────────────────────────────────

@login_required
@admin_or_above_required
def user_list(request):
    """
    Display paginated list of all users with search and filtering.

    GET Parameters:
        - q       : Search query (name, email, username, department)
        - role    : Filter by role name
        - status  : Filter by account status
        - page    : Page number for pagination
    """
    users = User.objects.select_related('role').order_by('full_name')
    roles = Role.objects.all()

    # ── Search ────────────────────────────────────────────────
    search_query = request.GET.get('q', '').strip()
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query)   |
            Q(email__icontains=search_query)        |
            Q(username__icontains=search_query)     |
            Q(department__icontains=search_query)
        )

    # ── Filter by Role ─────────────────────────────────────────
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role__role_name=role_filter)

    # ── Filter by Status ───────────────────────────────────────
    status_filter = request.GET.get('status', '')
    if status_filter:
        users = users.filter(status=status_filter)

    # ── Pagination ─────────────────────────────────────────────
    paginator    = Paginator(users, getattr(settings, 'ITEMS_PER_PAGE', 10))
    page_number  = request.GET.get('page', 1)
    page_obj     = paginator.get_page(page_number)

    context = {
        'page_obj':      page_obj,
        'roles':         roles,
        'search_query':  search_query,
        'role_filter':   role_filter,
        'status_filter': status_filter,
        'total_users':   users.count(),
        'page_title':    'User Management',
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@admin_or_above_required
def user_create(request):
    """
    Create a new user account (Admin only).

    GET:  Display blank user creation form.
    POST: Validate and save new user with hashed password.
    """
    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'User "{user.full_name}" created successfully.'
            )
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreateForm()

    return render(request, 'accounts/user_form.html', {
        'form':       form,
        'form_title': 'Create New User',
        'page_title': 'Create User',
        'action':     'Create',
    })


@login_required
@admin_or_above_required
def user_update(request, pk):
    """
    Update an existing user account.

    Only Super Admin can update another Super Admin's account.
    Admin cannot update their own role.
    """
    user_obj = get_object_or_404(User, pk=pk)

    # Prevent non-Super Admin from editing Super Admin accounts
    if (user_obj.is_super_admin() and not request.user.is_super_admin()):
        messages.error(request, 'You do not have permission to edit a Super Admin account.')
        return redirect('accounts:user_list')

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'User "{user_obj.full_name}" updated successfully.'
            )
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=user_obj)

    return render(request, 'accounts/user_form.html', {
        'form':       form,
        'form_title': f'Update User: {user_obj.full_name}',
        'page_title': 'Update User',
        'action':     'Update',
        'user_obj':   user_obj,
    })


@login_required
@admin_or_above_required
def user_delete(request, pk):
    """
    Soft-delete (deactivate) a user account.

    We never hard-delete users to preserve audit trail integrity.
    Instead, the account status is set to Inactive.
    """
    user_obj = get_object_or_404(User, pk=pk)

    # Prevent deleting own account
    if user_obj == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('accounts:user_list')

    # Prevent non-Super Admin from deleting Super Admin
    if user_obj.is_super_admin() and not request.user.is_super_admin():
        messages.error(request, 'You do not have permission to deactivate a Super Admin.')
        return redirect('accounts:user_list')

    if request.method == 'POST':
        user_obj.deactivate()
        messages.success(
            request,
            f'User "{user_obj.full_name}" has been deactivated successfully.'
        )
        return redirect('accounts:user_list')

    return render(request, 'accounts/user_confirm_delete.html', {
        'user_obj':   user_obj,
        'page_title': 'Deactivate User',
    })


@login_required
def user_detail(request, pk):
    """Display detailed profile of a user."""
    user_obj = get_object_or_404(User.objects.select_related('role'), pk=pk)
    return render(request, 'accounts/user_detail.html', {
        'user_obj':   user_obj,
        'page_title': f'User Profile: {user_obj.full_name}',
    })


# ──────────────────────────────────────────────────────────────
# PROFILE & PASSWORD VIEWS
# ──────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    """
    Unified profile page with three tabs: Edit Profile, Security, Account Actions.

    POST form_type='profile'  → update name/phone/gender/department/pic
    POST form_type='password' → change password inline (no separate page)
    GET                       → display both forms pre-populated
    """
    profile_form  = ProfileUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            profile_form = ProfileUpdateForm(
                request.POST, request.FILES, instance=request.user
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the errors in your profile.')
                return redirect(request.path + _TAB_ANCHOR['profile'])

        elif form_type == 'password':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the password errors.')
                return redirect(request.path + _TAB_ANCHOR['password'])

    return render(request, 'accounts/profile.html', {
        'form':          profile_form,
        'password_form': password_form,
        'page_title':    'My Profile',
    })


@login_required
def change_password(request):
    """
    Standalone change-password page (still accessible via direct URL).
    Redirects to profile security tab instead to keep UI unified.
    """
    return redirect('accounts:profile')


@login_required
def resign_view(request):
    """
    Dedicated resign page (GET) and resign action (POST).

    GET:  Render the full resign confirmation page (resign.html).
    POST: Deactivate account, log user out, redirect to login with message.
    """
    if request.method == 'POST':
        user = request.user
        user.deactivate()          # sets status=Inactive, is_active=False
        logout(request)
        messages.success(
            request,
            'Your account has been deactivated. '
            'Please contact an administrator to re-activate it.'
        )
        return redirect('accounts:login')

    # GET — show the resign confirmation page
    return render(request, 'accounts/resign.html', {
        'page_title': 'Resign from EIAMS',
    })
