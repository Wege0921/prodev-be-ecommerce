from django.contrib import admin
from .models import Category, Product, Order, OrderItem


class OrderItemInline(admin.TabularInline): 
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "total_amount")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    inlines = [OrderItemInline]

    def total_amount(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    total_amount.short_description = "Total Amount"


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "item_total")

    def item_total(self, obj):
        return obj.product.price * obj.quantity
    item_total.short_description = "Item Total"


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
