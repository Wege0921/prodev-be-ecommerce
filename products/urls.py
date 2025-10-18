from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, ContactMessageViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"contact", ContactMessageViewSet, basename="contact")

urlpatterns = [
    path("", include(router.urls)),
]