"""
Accounts Forms - EIAMS
======================
Defines all forms for user authentication and management.

Forms:
    - LoginForm          : User login (username/email + password)
    - UserCreateForm     : Admin creates a new user
    - UserUpdateForm     : Admin or user updates profile
    - PasswordChangeForm : User changes their own password
    - PasswordResetForm  : Request password reset email
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User, Role


class LoginForm(AuthenticationForm):
    """
    User login form with Bootstrap 5 styling.
    Accepts username or email for login flexibility.

    Inherits from Django's AuthenticationForm which handles
    credential validation and CSRF protection automatically.
    """

    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter your username',
            'autofocus':   True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter your password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Remember me for 30 days',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model  = User
        fields = ['username', 'password']


class UserCreateForm(forms.ModelForm):
    """
    Form for creating a new user account.
    Used by Admin/Super Admin only.

    Includes password confirmation field and role assignment.
    """

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter password',
        }),
        help_text='Minimum 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Confirm password',
        })
    )

    class Meta:
        model  = User
        fields = [
            'full_name', 'username', 'email', 'gender',
            'phone', 'department', 'role', 'status', 'profile_pic'
        ]
        widgets = {
            'full_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'username':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'gender':     forms.Select(attrs={'class': 'form-select'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
            'status':     forms.Select(attrs={'class': 'form-select'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        """Validate that both password fields match."""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match.')
        if p1 and len(p1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        return p2

    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        """Validate username uniqueness."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username

    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # Sync full_name to first_name for Django auth compatibility
        names = self.cleaned_data['full_name'].split(' ', 1)
        user.first_name = names[0]
        user.last_name  = names[1] if len(names) > 1 else ''
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for Admin to update user account details.
    Does not include password fields (use PasswordChangeForm instead).
    """

    class Meta:
        model  = User
        fields = [
            'full_name', 'username', 'email', 'gender',
            'phone', 'department', 'role', 'status', 'profile_pic'
        ]
        widgets = {
            'full_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'username':    forms.TextInput(attrs={'class': 'form-control'}),
            'email':       forms.EmailInput(attrs={'class': 'form-control'}),
            'gender':      forms.Select(attrs={'class': 'form-select'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control'}),
            'department':  forms.TextInput(attrs={'class': 'form-control'}),
            'role':        forms.Select(attrs={'class': 'form-select'}),
            'status':      forms.Select(attrs={'class': 'form-select'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        """Validate email uniqueness excluding current user."""
        email = self.cleaned_data.get('email')
        qs    = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        """Validate username uniqueness excluding current user."""
        username = self.cleaned_data.get('username')
        qs       = User.objects.filter(username=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('A user with this username already exists.')
        return username


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for users to update their OWN profile.
    Limited fields: no role or status changes allowed.
    Users can only change: full_name, phone, gender, department, profile_pic.
    """

    class Meta:
        model  = User
        fields = ['full_name', 'phone', 'gender', 'department', 'profile_pic']
        widgets = {
            'full_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control'}),
            'gender':      forms.Select(attrs={'class': 'form-select'}),
            'department':  forms.TextInput(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    """
    Password change form for authenticated users.
    Requires current password before setting new one.
    Inherits Django's PasswordChangeForm for secure handling.
    """

    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password',
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter new password',
        }),
        help_text='Minimum 8 characters.'
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Confirm new password',
        })
    )
