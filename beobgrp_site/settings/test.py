"""
Test settings - uses SQLite instead of PostgreSQL for testing
"""
from .base import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable debug during tests
DEBUG = False

# Speed up password hashing during tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable compressor during tests
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# Use simple media storage for tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Disable dbbackup during tests
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/tmp/'}
