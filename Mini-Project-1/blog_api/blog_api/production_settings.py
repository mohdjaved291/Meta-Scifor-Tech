from .settings import *
import os

# SECURITY WARNING: change this in production!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-@2gfxggu9tmb@pyz@!r#-med%d7gwt1guj^%j%9cemv$6%r$*n",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update this with your actual PythonAnywhere username
ALLOWED_HOSTS = ["mohdjaved25.pythonanywhere.com", "localhost", "127.0.0.1"]

# Static files settings for PythonAnywhere
STATIC_URL = "/static/"
STATIC_ROOT = "/home/mohdjaved25/Mini-Project-1/blog_api/staticfiles"

# Media files settings
MEDIA_URL = "/media/"
MEDIA_ROOT = "/home/mohdjaved25/Mini-Project-1/blog_api/media"

# Update static files dirs
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://mohdjaved25.pythonanywhere.com",
]

# Override CORS settings for production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # More secure for production

# CSRF settings for production
CSRF_TRUSTED_ORIGINS = [
    "https://mohdjaved25.pythonanywhere.com",
]

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Database - keeping SQLite for free tier
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Logging for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/home/mohdjaved25/Mini-Project-1/blog_api/django.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
