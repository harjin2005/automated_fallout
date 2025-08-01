from .settings import *
import os

# Production settings
DEBUG = False

ALLOWED_HOSTS = [
    'fallout-room-backend.onrender.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',  # Critical for Render
]

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://harjin2005.github.io",
]
CORS_ALLOW_ALL_ORIGINS = True

# Critical for Render deployment
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Ensure proper host binding for Render
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
