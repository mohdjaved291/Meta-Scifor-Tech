from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"posts", views.PostViewSet)

urlpatterns = [
    # Only API endpoints - no frontend views
    path("api/", include(router.urls)),
]
