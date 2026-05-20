"""
Django Settings for Student Management System
==============================================

WHY THIS FILE EXISTS:
    This is the central configuration hub for the entire Django project.
    Every setting — database, security, installed apps, templates,
    static files — lives here.

HOW IT CONNECTS:
    - manage.py points to this file via DJANGO_SETTINGS_MODULE
    - Every Django component reads its configuration from here
    - wsgi.py and asgi.py also reference this module

DESIGN DECISIONS:
    1. python-decouple reads secrets from .env (never hardcoded)
    2. Apps are split into DJANGO_APPS, THIRD_PARTY_APPS, LOCAL_APPS
       for clarity as the project grows
    3. Static/media config is production-ready with WhiteNoise
    4. Database is SQLite for development, easily swappable to PostgreSQL
"""

from pathlib import Path
from decouple import config, Csv
from django.contrib.messages import constants as messages

# =============================================================
# PATH CONFIGURATION
# =============================================================
# BASE_DIR points to the project root (where manage.py lives)
# All other paths are relative to this.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================
# SECURITY
# =============================================================
# SECRET_KEY: Used for cryptographic signing (sessions, CSRF, etc.)
# NEVER hardcode this in production — always use .env
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-me')

# DEBUG: Shows detailed error pages. MUST be False in production.
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS: Domains this site can serve. Empty = localhost only.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver', cast=Csv())

# =============================================================
# APPLICATION DEFINITION
# =============================================================
# Split into three groups for maintainability:
#   - DJANGO_APPS:      Built-in Django functionality
#   - THIRD_PARTY_APPS: Installed via pip
#   - LOCAL_APPS:        Our custom apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',      # Adds template filters like intcomma
]

THIRD_PARTY_APPS = [
    'crispy_forms',                  # DRY, beautiful forms
    'crispy_bootstrap5',             # Bootstrap 5 template pack
    'rest_framework',                # Django REST Framework for API
    'rest_framework_simplejwt',      # JWT Authentication
]

LOCAL_APPS = [
    'apps.accounts.apps.AccountsConfig',
    'apps.students.apps.StudentsConfig',
    'apps.academics.apps.AcademicsConfig',
    'apps.enrollments.apps.EnrollmentsConfig',
    'apps.assessments.apps.AssessmentsConfig',
    'apps.communication.apps.CommunicationConfig',
    'apps.api.apps.ApiConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================
# MIDDLEWARE
# =============================================================
# Middleware processes every request/response in order.
# WhiteNoise is placed right after SecurityMiddleware to
# serve static files efficiently in production.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =============================================================
# URL CONFIGURATION
# =============================================================
ROOT_URLCONF = 'config.urls'

# =============================================================
# TEMPLATE CONFIGURATION
# =============================================================
# DIRS: We use a project-level templates/ folder (not per-app)
# so all templates live in one place with clear structure.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.accounts.context_processors.user_profile',
            ],
        },
    },
]

# =============================================================
# WSGI / ASGI
# =============================================================
WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================
# DATABASE
# =============================================================
# SQLite for development — no setup required.
# To switch to PostgreSQL, install psycopg2-binary and update:
#
#   DATABASES = {
#       'default': {
#           'ENGINE': 'django.db.backends.postgresql',
#           'NAME': config('DB_NAME'),
#           'USER': config('DB_USER'),
#           'PASSWORD': config('DB_PASSWORD'),
#           'HOST': config('DB_HOST', default='localhost'),
#           'PORT': config('DB_PORT', default='5432'),
#       }
#   }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================
# PASSWORD VALIDATION
# =============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================
# INTERNATIONALIZATION
# =============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================
# STATIC_URL: URL prefix for static files in templates
# STATICFILES_DIRS: Where Django looks for static files during development
# STATIC_ROOT: Where collectstatic gathers files for production
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise compression and caching for production
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# =============================================================
# MEDIA FILES (User-uploaded content)
# =============================================================
# MEDIA_URL: URL prefix for uploaded files
# MEDIA_ROOT: Filesystem path where uploads are saved
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================
# AUTHENTICATION
# =============================================================
# Where to redirect after login/logout
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'students:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# =============================================================
# CRISPY FORMS
# =============================================================
# Use Bootstrap 5 template pack for all crispy-rendered forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# =============================================================
# MESSAGES FRAMEWORK
# =============================================================
# Map Django message levels to Bootstrap CSS classes

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# =============================================================
# DEFAULT PRIMARY KEY
# =============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================
# EMAIL BACKEND (Console for development)
# =============================================================
# Prints emails to the terminal instead of sending them.
# Switch to SMTP for production.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================
# REST FRAMEWORK
# =============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
