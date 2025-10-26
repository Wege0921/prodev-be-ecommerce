from rest_framework import serializers
from .models import Product, Category, Order, OrderItem, ContactMessage
from django.db import transaction
from django.db.models import F
from django.conf import settings
from .tasks import send_order_telegram

class CategorySerializer(serializers.ModelSerializer):
    children_count = serializers.IntegerField(read_only=True)
    has_children = serializers.BooleanField(read_only=True)
    class Meta:
        model = Category
        fields = ["id", "name", "parent", "children_count", "has_children", "created_at"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Category.objects.all(), source="category")
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "stock",
            "image_url",
            "is_featured",
            "category",
            "category_id",
            "images",
            "created_at",
            "updated_at",
        ]

    def get_images(self, obj):
        # Return list of ProductImage URLs; fall back to single image_url if set
        urls = [img.url for img in getattr(obj, 'images').all()] if hasattr(obj, 'images') else []
        if not urls and getattr(obj, 'image_url', ''):
            urls = [obj.image_url]
        return urls

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "created_at",
            "status",
            "delivery_address",
            "payment_proof_url",
            "items",
        ]
        read_only_fields = ["user", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        with transaction.atomic():
            order = Order.objects.create(user=user, **validated_data)

            for item_data in items_data:
                product = item_data.get("product") or Product.objects.get(id=item_data["product_id"])  # ensure product exists
                quantity = item_data.get("quantity", 1)

                # Update stock with safety check
                updated = Product.objects.filter(id=product.id, stock__gte=quantity).update(stock=F("stock") - quantity)
                if not updated:
                    raise serializers.ValidationError(
                        {"stock": f"Insufficient stock for product '{product.title}'."}
                    )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )

        # Enqueue Telegram notification after commit
        transaction.on_commit(lambda: send_order_telegram.delay(order.id))

        return order


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "subject",
            "message",
            "created_at",
            "is_resolved",
        ]
        read_only_fields = ["created_at", "is_resolved"]