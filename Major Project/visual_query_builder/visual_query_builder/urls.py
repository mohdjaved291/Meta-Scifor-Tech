"""
URL configuration for visual_query_builder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for visual_query_builder project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_info(request):
    """Simple API info page instead of template"""
    return JsonResponse(
        {
            "app": "Visual Database Query Builder",
            "status": "running",
            "version": "1.0",
            "endpoints": {
                "admin": "/admin/",
                "api_connections": "/api/connections/",
                "api_schema": "/api/connections/{id}/schema/",
                "create_sample_data": "/api/create-sample-data/",
                "query_build": "/api/query/build/",
                "query_execute": "/api/query/execute/",
            },
            "usage": "This is the backend API for the Visual Database Query Builder",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("query_builder.urls")),
    path("", api_info, name="home"),  # Changed from TemplateView to simple JSON
]
