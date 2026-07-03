"""
Django production settings for pouriabaghban3 project.

This file overrides development settings for production environments.
Use with: DJANGO_SETTINGS_MODULE=pouriabaghban3.settings_production
"""

import os
from pathlib import Path
from pouriabaghban3.settings import *  # noqa

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Change this in production!
# Generate a new secret key using: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production!")

# Disable debug mode in production
DEBUG = False

# Set your domain(s) here
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'pouriabaghban.ir,www.pouriabaghban.ir,.pouriabaghban.ir,.runflare.com,.runflare.app,localhost,127.0.0.1',
)
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS.split(',') if host.strip()]

# Secure cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://pouriabaghban.ir,https://www.pouriabaghban.ir,https://*.pouriabaghban.ir,https://*.runflare.com,https://*.runflare.app',
)
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS.split(',') if origin.strip()]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_FAILURE_VIEW = "pages.views.csrf_failure"

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Use PostgreSQL in production (recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'pouriabaghban3'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# ============================================================================
# STATIC AND MEDIA FILES
# ============================================================================

# Static files served by web server (nginx/apache)
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')

# Media files for user uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

# ============================================================================
# CACHING
# ============================================================================

# Use Redis for caching (recommended)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# ============================================================================
# ADMIN URL (Change default /admin/ path)
# ============================================================================

# Uncomment to change admin URL to something more secure
# ADMIN_URL = os.environ.get('ADMIN_URL', 'secure-admin-path/')

# ============================================================================
# PERFORMANCE OPTIMIZATIONS
# ============================================================================

# Gzip compression
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pouriabaghban3.middleware.AdminSecurityMiddleware',
]

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# ============================================================================
# ERROR TRACKING (Optional)
# ============================================================================

# Uncomment to use Sentry for error tracking
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# SENTRY_DSN = os.environ.get('SENTRY_DSN')
# if SENTRY_DSN:
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,
#         send_default_pii=False
#     )

# ============================================================================
# ADMIN CONFIGURATION
# ============================================================================

ADMINS = [
    ('Admin Name', os.environ.get('ADMIN_EMAIL', 'poriab426@gmail.com')),
]

MANAGERS = ADMINS

# ============================================================================
# ALLOWED FILE UPLOADS
# ============================================================================

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
