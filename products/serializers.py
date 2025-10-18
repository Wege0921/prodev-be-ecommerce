from rest_framework import serializers
from .models import Product, Category, Order, OrderItem, ContactMessage
from django.db import transaction
from django.db.models import F

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Category.objects.all(), source="category")

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
            "created_at",
            "updated_at",
        ]

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
                product = item_data["product"]
                quantity = int(item_data["quantity"])  # ensure int

                if quantity <= 0:
                    raise serializers.ValidationError({"quantity": "Quantity must be greater than 0."})

                # Attempt atomic stock decrement only if enough stock
                updated = Product.objects.filter(
                    pk=product.pk,
                    stock__gte=quantity,
                ).update(stock=F("stock") - quantity)

                if updated == 0:
                    raise serializers.ValidationError(
                        {"stock": f"Insufficient stock for product '{product.title}'."}
                    )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )

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