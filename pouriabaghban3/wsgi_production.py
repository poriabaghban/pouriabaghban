#!/usr/bin/env python
"""
WSGI config for pouriabaghban3 project for production.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# Set the default Django settings module for production
# Can be overridden by DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings_production')

# Create the WSGI application
application = get_wsgi_application()

# For production with whitenoise for static file serving
try:
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(application)
except ImportError:
    pass
