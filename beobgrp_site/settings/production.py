from .base import *
import os
from urllib.parse import urlparse

DEBUG = False

# Get the secret key from an environment variable
# Make sure to set this in your production environment!
SECRET_KEY = os.environ.get('SECRET_KEY')

# If SECRET_KEY is not set in a production environment, raise an error
if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable must be set in production.")

# Get the hostname from the WAGTAILADMIN_BASE_URL to automatically add it to allowed hosts
base_url = urlparse(WAGTAILADMIN_BASE_URL)
allowed_host = base_url.hostname or 'localhost'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    allowed_host,
    '.beobachtergruppe.de',
]

# Add the production domain to CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    f"https://{allowed_host}",
    "https://www.beobachtergruppe.de",  # Include the www version for compatibility
]

# In production, these should all be True. For local testing over HTTP, they can be disabled.
use_secure_ssl = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "true").lower() == "true"

# Security settings for production
CSRF_COOKIE_SECURE = use_secure_ssl
SESSION_COOKIE_SECURE = use_secure_ssl
SECURE_SSL_REDIRECT = use_secure_ssl

# Configure logging for production to be less verbose
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'wagtail': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'beobgrp_site': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

try:
    from .local import *
except ImportError:
    pass
