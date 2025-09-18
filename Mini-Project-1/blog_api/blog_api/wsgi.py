"""
WSGI config for blog_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Add your project directory to Python path
path = "/home/mohdjaved25/Mini-Project-1/blog_api"  # Replace 'yourusername' with your PythonAnywhere username
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ["DJANGO_SETTINGS_MODULE"] = "blog_api.production_settings"

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
