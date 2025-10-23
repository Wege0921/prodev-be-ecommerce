import django_filters
from django_filters import rest_framework as filters
from .models import Product, Category

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = filters.NumberFilter(method="filter_category")
    in_stock = filters.BooleanFilter(method="filter_in_stock")
    is_featured = filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Product
        fields = ["category", "price_min", "price_max", "in_stock", "is_featured"]

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock__gt=0)
        if value is False:
            return queryset.filter(stock__lte=0)
        return queryset

    def filter_category(self, queryset, name, value):
        # value is the category id passed in query string
        try:
            cid = int(value)
        except (TypeError, ValueError):
            return queryset
        request = getattr(self, 'request', None)
        descendants_param = None
        if request is not None:
            descendants_param = request.query_params.get('descendants')
        if descendants_param and str(descendants_param).lower() in {"1", "true", "yes"}:
            # BFS to collect all descendant ids including the root
            to_visit = [cid]
            seen = set()
            all_ids = set()
            while to_visit:
                current = to_visit.pop(0)
                if current in seen:
                    continue
                seen.add(current)
                all_ids.add(current)
                children = list(Category.objects.filter(parent_id=current).values_list('id', flat=True))
                to_visit.extend(children)
            return queryset.filter(category_id__in=list(all_ids))
        # default: exact match
        return queryset.filter(category_id=cid)
