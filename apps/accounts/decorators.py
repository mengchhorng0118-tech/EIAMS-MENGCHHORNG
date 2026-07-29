"""
Role-Based Access Control Decorators - EIAMS
=============================================
These decorators protect views by enforcing role-based access control.
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

_LOGIN_URL = reverse_lazy('accounts:login')


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url=_LOGIN_URL)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.role:
                messages.error(request, 'Your account has no role assigned. Please contact the administrator.')
                return redirect('dashboard:home')
            if request.user.role.role_name not in allowed_roles:
                messages.error(request, f'Access denied. Required roles: {", ".join(allowed_roles)}.')
                return redirect('dashboard:home')
            if request.user.status == 'Inactive':
                messages.error(request, 'Your account has been deactivated.')
                return redirect('accounts:login')
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def super_admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url=_LOGIN_URL)
    def wrapped_view(request, *args, **kwargs):
        if not (request.user.role and request.user.role.role_name == 'Super Admin'):
            messages.error(request, 'Access denied. Super Admin privileges required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def admin_or_above_required(view_func):
    @wraps(view_func)
    @login_required(login_url=_LOGIN_URL)
    def wrapped_view(request, *args, **kwargs):
        allowed = ['Super Admin', 'Admin']
        if not (request.user.role and request.user.role.role_name in allowed):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def manager_or_above_required(view_func):
    @wraps(view_func)
    @login_required(login_url=_LOGIN_URL)
    def wrapped_view(request, *args, **kwargs):
        allowed = ['Super Admin', 'Admin', 'Manager']
        if not (request.user.role and request.user.role.role_name in allowed):
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def active_user_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == 'Inactive':
            messages.error(request, 'Your account has been deactivated.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapped_view
