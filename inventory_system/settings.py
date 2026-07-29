"""
Django Settings for Enterprise Inventory & Asset Management System (EIAMS)
=========================================================================
Author: EIAMS Development Team
Course: System Analysis & Design (SAD) - BIU Y3S1IT
Date: July 2026

This file configures the entire Django project including:
- Database configuration (SQLite for development, MySQL for production)
- Installed apps (built-in + third-party + custom apps)
- Template and static file settings
- Authentication backends and session management
- Media file handling for uploads
"""

from pathlib import Path
import os

# ============================================================
# BASE DIRECTORY CONFIGURATION
# ============================================================
# Build paths inside the project like: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# SECURITY SETTINGS
# ============================================================
# SECURITY WARNING: Keep the secret key secret in production!
SECRET_KEY = 'django-insecure-eiams-secret-key-change-in-production-biu-sad-2026'

# SECURITY WARNING: Don't run with debug turned on in production!
DEBUG = False


# Hosts allowed to serve this application
# ALLOWED_HOSTS = ['*']  # Restrict to specific domain in production
ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]
# ============================================================
# INSTALLED APPLICATIONS
# ============================================================
INSTALLED_APPS = [
    # Django Built-in Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # For number formatting in templates

    # Third-Party Apps
    'crispy_forms',            # Enhanced form rendering
    'crispy_bootstrap5',       # Bootstrap 5 form theme
    'widget_tweaks',           # Template form widget customization

    # Custom Application Modules
    'apps.accounts',           # User Authentication & Role Management
    'apps.inventory',          # Inventory Item & Category Management
    'apps.assets',             # Asset Lifecycle Management
    'apps.stock',              # Stock Movements & Low Stock Alerts
    'apps.notifications',      # In-App Notification System
    'apps.reports',            # Report Generation Module
    'apps.dashboard',          # Dashboard & KPI Analytics
]

# ============================================================
# MIDDLEWARE CONFIGURATION
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',          # i18n language detection
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URL CONFIGURATION
# ============================================================
ROOT_URLCONF = 'inventory_system.urls'

# ============================================================
# TEMPLATE CONFIGURATION
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Global templates directory
        ],
        'APP_DIRS': True,  # Also load templates from app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.notifications.context_processors.notification_count',
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'inventory_system.wsgi.application'

# ============================================================
# DATABASE CONFIGURATION
# ============================================================
# Default: SQLite for development/assignment use
# Switch to MySQL for production deployment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    # MySQL Production Configuration (uncomment when needed):
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'eiams_db',
    #     'USER': 'root',
    #     'PASSWORD': 'your_password',
    #     'HOST': 'localhost',
    #     'PORT': '3306',
    #     'OPTIONS': {'charset': 'utf8mb4'},
    # }
}

# ============================================================
# CUSTOM USER MODEL
# ============================================================
# We extend Django's AbstractUser for our custom User model
AUTH_USER_MODEL = 'accounts.User'

# ============================================================
# PASSWORD VALIDATION
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# AUTHENTICATION SETTINGS
# ============================================================
LOGIN_URL          = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Session timeout: 120 minutes (7200 seconds) as per requirements
SESSION_COOKIE_AGE = 7200             # 2 hours idle timeout
SESSION_SAVE_EVERY_REQUEST = True     # Reset session timer on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ============================================================
# INTERNATIONALIZATION
# ============================================================
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Phnom_Penh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en',  _('English')),
    ('km',  _('ខ្មែរ')),   # Khmer
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ============================================================
# STATIC FILES (CSS, JavaScript, Images)
# ============================================================
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     BASE_DIR / 'static',  # Development static files
# ]
# STATIC_ROOT = BASE_DIR / 'staticfiles'  # Production static files (collectstatic)
STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ============================================================
# MEDIA FILES (User Uploads)
# ============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CRISPY FORMS CONFIGURATION (Bootstrap 5)
# ============================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============================================================
# MESSAGE FRAMEWORK CONFIGURATION
# ============================================================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ============================================================
# EMAIL CONFIGURATION (Development: console backend)
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For production SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your@email.com'
# EMAIL_HOST_PASSWORD = 'your_password'

# ============================================================
# PAGINATION SETTINGS
# ============================================================
ITEMS_PER_PAGE = 10  # Default items per page for list views

# ============================================================
# LOW STOCK ALERT THRESHOLD
# ============================================================
# Defined per item via min_qty field, alert triggered when
# current_qty <= min_qty (handled via Django signals)
