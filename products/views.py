# products/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import requests
from .models import Product, Category, Order, ContactMessage
from .serializers import ProductSerializer, CategorySerializer,  OrderSerializer, ContactMessageSerializer
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
        # Build URL
        url = request.build_absolute_uri(settings.MEDIA_URL + path.split(settings.MEDIA_ROOT + '/')[-1]) if getattr(settings, 'MEDIA_URL', None) else path
        order.payment_proof_url = url
        order.save(update_fields=["payment_proof_url"])
        return Response({"payment_proof_url": url}, status=200)


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

        # Telegram webhook notification if configured
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        if bot_token and chat_id:
            try:
                text = (
                    f"New Contact Message\n"
                    f"From: {msg.name}\n"
                    f"Phone: {msg.phone or '-'}\n"
                    f"Email: {msg.email or '-'}\n"
                    f"Subject: {msg.subject}\n"
                    f"Message: {msg.message}"
                )
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={"chat_id": chat_id, "text": text},
                    timeout=6,
                )
            except Exception:
                pass

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
