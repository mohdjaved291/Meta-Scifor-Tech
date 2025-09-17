from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"books", views.BookViewSet)
router.register(r"borrow-records", views.BorrowRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
