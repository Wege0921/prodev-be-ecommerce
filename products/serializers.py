from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Category.objects.all(), source="category")

    class Meta:
        model = Product
        fields = ["id", "title", "description", "price", "stock", "category", "category_id", "created_at", "updated_at"]
