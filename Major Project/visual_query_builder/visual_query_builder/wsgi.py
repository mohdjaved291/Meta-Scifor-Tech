"""
WSGI config for visual_query_builder project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

project_home = "/home/mohdjaved25/visual-query-builder"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ["DJANGO_SETTINGS_MODULE"] = "visual_query_builder.production_settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
