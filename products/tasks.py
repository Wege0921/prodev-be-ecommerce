from celery import shared_task
import requests
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Order, ContactMessage

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=60, max_retries=5)
def send_order_telegram(self, order_id: int):
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    if not (bot_token and chat_id):
        logger.info("Telegram credentials not configured; skipping notification for order %s", order_id)
        return
    order = Order.objects.filter(id=order_id).first()
    if not order:
        logger.warning("Order %s not found for telegram notification", order_id)
        return
    user = order.user
    item_count = order.items.count()
    text = (
        f"New Order #{order.id}\n"
        f"User: {getattr(user, 'username', str(user))}\n"
        f"Items: {item_count}\n"
        f"Status: {order.status}\n"
        f"Created: {order.created_at:%Y-%m-%d %H:%M:%S}\n"
        f"Address: {order.delivery_address or '-'}\n"
        f"Proof: {'Yes' if order.payment_proof_url else 'No'}"
    )
    r = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    if r.status_code >= 400:
        logger.warning("Telegram sendMessage(new order) failed: %s %s", r.status_code, r.text)
        r.raise_for_status()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=60, max_retries=5)
def send_contact_telegram(self, message_id: int):
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    if not (bot_token and chat_id):
        logger.info("Telegram credentials not configured; skipping contact notification %s", message_id)
        return
    msg = ContactMessage.objects.filter(id=message_id).first()
    if not msg:
        logger.warning("ContactMessage %s not found for telegram notification", message_id)
        return
    text = (
        f"New Contact Message\n"
        f"From: {msg.name}\n"
        f"Phone: {msg.phone or '-'}\n"
        f"Email: {msg.email or '-'}\n"
        f"Subject: {msg.subject}\n"
        f"Message: {msg.message}"
    )
    r = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    if r.status_code >= 400:
        logger.warning("Telegram sendMessage(contact) failed: %s %s", r.status_code, r.text)
        r.raise_for_status()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=60, max_retries=3)
def process_payment_proof(self, order_id: int, proof_url: str):
    # Placeholder for image processing (e.g., compress/scan/thumbnail). Currently no-op.
    logger.info("Processing payment proof for order %s at %s", order_id, proof_url)
    return True
