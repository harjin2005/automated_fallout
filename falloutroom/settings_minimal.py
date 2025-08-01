from .settings import *

# Minimal production settings
DEBUG = True  # Temporary for debugging
ALLOWED_HOSTS = ['*']

# Use SQLite for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Allow all CORS origins
CORS_ALLOW_ALL_ORIGINS = True

# Disable SSL redirect
SECURE_SSL_REDIRECT = False
