from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category


def _clear_cache(reason: str):
    # Pragmatic approach: clear all API caches to avoid stale lists quickly.
    # Can be refined to targeted keys later.
    try:
        cache.clear()
    except Exception:
        pass


@receiver(post_save, sender=Product)
def product_saved(sender, instance: Product, created, **kwargs):
    _clear_cache("product_saved")


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance: Product, **kwargs):
    _clear_cache("product_deleted")


@receiver(post_save, sender=Category)
def category_saved(sender, instance: Category, created, **kwargs):
    _clear_cache("category_saved")


@receiver(post_delete, sender=Category)
def category_deleted(sender, instance: Category, **kwargs):
    _clear_cache("category_deleted")
