"""
WSGI config for visual_query_builder project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use render_settings for production deployment on Render
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visual_query_builder.render_settings")

application = get_wsgi_application()
