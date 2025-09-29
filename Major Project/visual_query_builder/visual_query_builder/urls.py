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
# visual_query_builder/urls.py - Main URLs file
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import JsonResponse


def api_health_check(request):
    """Simple health check for API"""
    return JsonResponse(
        {
            "status": "OK",
            "message": "Visual Query Builder API is running",
            "available_endpoints": [
                "/api/connections/",
                "/api/query/build/",
                "/api/query/execute/",
                "/api/create-sample-data/",
            ],
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints - this MUST come first
    path("api/", include("query_builder.urls")),
    # Health check
    path("api-health/", api_health_check, name="api-health"),
    # Serve React app (fallback)
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    # Catch-all for React Router (if using client-side routing)
    path(
        "<path:path>/",
        TemplateView.as_view(template_name="index.html"),
        name="react-routes",
    ),
]
