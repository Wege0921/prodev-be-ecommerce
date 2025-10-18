from django.core.management.base import BaseCommand
from products.models import Category, Product

class Command(BaseCommand):
    help = "Seed the database with sample categories and products."

    def handle(self, *args, **options):
        categories = [
            ("Electronics", [
                {"title": "Smartphone", "price": 499.99, "stock": 25, "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800"},
                {"title": "Laptop", "price": 1199.00, "stock": 10, "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800"},
                {"title": "Headphones", "price": 79.99, "stock": 50, "image_url": "https://images.unsplash.com/photo-1518444075430-7db54d7e12a9?w=800"},
            ]),
            ("Home", [
                {"title": "Vacuum Cleaner", "price": 149.99, "stock": 15, "image_url": "https://images.unsplash.com/photo-1598300053656-01a6526ddfd2?w=800"},
                {"title": "Blender", "price": 39.99, "stock": 30, "image_url": "https://images.unsplash.com/photo-1603031613617-9e14c9b5d1b0?w=800"},
            ]),
            ("Books", [
                {"title": "Django for APIs", "price": 29.99, "stock": 100, "image_url": "https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=800"},
                {"title": "Clean Code", "price": 34.99, "stock": 40, "image_url": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?w=800"},
            ]),
        ]

        created_counts = {"categories": 0, "products": 0}

        for cat_name, items in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                created_counts["categories"] += 1
            for item in items:
                product, p_created = Product.objects.get_or_create(
                    title=item["title"],
                    defaults={
                        "description": item["title"],
                        "price": item["price"],
                        "stock": item["stock"],
                        "image_url": item.get("image_url", ""),
                        "is_featured": item["title"] in {"Smartphone", "Laptop", "Clean Code"},
                        "category": category,
                    },
                )
                if p_created:
                    created_counts["products"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Categories created: {created_counts['categories']}, Products created: {created_counts['products']}"
        ))
