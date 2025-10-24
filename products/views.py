# products/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import requests
import logging
from django.db.models import Count, Case, When, BooleanField
from .models import Product, Category, Order, ContactMessage
from .serializers import ProductSerializer, CategorySerializer,  OrderSerializer, ContactMessageSerializer
from .tasks import send_contact_telegram, process_payment_proof
from django.db import transaction
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

@method_decorator(cache_page(getattr(settings, 'CACHE_TTL', 300)), name="list")
@method_decorator(cache_page(getattr(settings, 'CACHE_TTL', 300)), name="retrieve")
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"

    def get_queryset(self):
        qs = Category.objects.all().annotate(children_count=Count("children"))
        qs = qs.annotate(
            has_children=Case(
                When(children_count__gt=0, then=True),
                default=False,
                output_field=BooleanField(),
            )
        )
        parent = self.request.query_params.get("parent")
        if parent is None:
            qs = qs.filter(parent__isnull=True)
        else:
            if parent == "":
                qs = qs.filter(parent__isnull=True)
            else:
                qs = qs.filter(parent_id=parent)
        return qs.order_by("name")


@method_decorator(cache_page(getattr(settings, 'CACHE_TTL', 120)), name="list")
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]
    search_fields = ["title", "description"]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
      
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
 
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_proof(self, request, pk=None):
        order = self.get_queryset().filter(pk=pk).first()
        if not order:
            return Response({"detail": "Not found."}, status=404)
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file provided."}, status=400)
        # Save to default storage
        path = default_storage.save(f"payment_proofs/order_{order.pk}_{file.name}", file)
        # Build URL using storage to support custom backends
        try:
            storage_url = default_storage.url(path)
            url = request.build_absolute_uri(storage_url)
        except Exception:
            url = path
        order.payment_proof_url = url
        order.save(update_fields=["payment_proof_url"])
        # enqueue optional post-processing in background
        transaction.on_commit(lambda: process_payment_proof.delay(order.id, url))
        return Response({"payment_proof_url": url}, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def set_status(self, request, pk=None):
        order = Order.objects.filter(pk=pk).first()
        if not order:
            return Response({"detail": "Not found."}, status=404)
        new_status = request.data.get("status", "").upper()
        allowed = {"PENDING", "PAID", "SHIPPED", "DELIVERED", "COMPLETED"}
        if new_status not in allowed:
            return Response({"detail": "Invalid status."}, status=400)
        # Simple transition rules (can be expanded):
        current = order.status
        transitions = {
            "PENDING": {"PAID", "CANCELLED"} if False else {"PAID", "SHIPPED", "DELIVERED", "COMPLETED"},
            "PAID": {"SHIPPED", "DELIVERED", "COMPLETED"},
            "SHIPPED": {"DELIVERED", "COMPLETED"},
            "DELIVERED": {"COMPLETED"},
            "COMPLETED": set(),
        }
        if new_status not in transitions.get(current, allowed):
            return Response({"detail": f"Transition {current} -> {new_status} not allowed."}, status=400)
        order.status = new_status
        order.save(update_fields=["status"])
        return Response({"id": order.id, "status": order.status}, status=200)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post", "get"]

    def get_queryset(self):
        # Only staff can list/read; public can create only
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return ContactMessage.objects.all()
        return ContactMessage.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        msg = serializer.save()

        # Enqueue Telegram notification via Celery after commit
        transaction.on_commit(lambda: send_contact_telegram.delay(msg.id))

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
