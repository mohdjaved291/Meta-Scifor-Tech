from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"posts", views.PostViewSet)

urlpatterns = [
    # Frontend view (serves the main blog interface)
    path("", views.frontend_view, name="frontend"),
    
    # Only API endpoints - no frontend views
    path("api/", include(router.urls)),
]
