from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ContactMessage


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "created_at")
    list_filter = ("parent", "created_at")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "stock", "is_featured", "created_at")
    list_filter = ("category", "is_featured", "created_at")
    search_fields = ("title",)
    list_editable = ("is_featured",)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "subject", "created_at", "is_resolved")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("name", "phone", "email", "subject")
