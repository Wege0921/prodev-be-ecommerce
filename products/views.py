# products/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAdminUser
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]
    search_fields = ["title", "description"]
