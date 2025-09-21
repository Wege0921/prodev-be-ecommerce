import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category_id")

    class Meta:
        model = Product
        fields = ["category", "price_min", "price_max"]
