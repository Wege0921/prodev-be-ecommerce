from celery import shared_task
import logging
import requests
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=60, max_retries=5)
def send_password_reset_notification(self, user_id: int):
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    if not (bot_token and chat_id):
        logger.info("Telegram not configured; skipping password reset notification for user %s", user_id)
        return

    user = User.objects.filter(id=user_id).first()
    if not user:
        logger.warning("User %s not found for password reset notification", user_id)
        return

    text = (
        f"Password/PIN Reset\n"
        f"User: {user.username or user.email or user.id}\n"
        f"This account's password/PIN was changed."
    )

    r = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    if r.status_code >= 400:
        logger.warning("Telegram sendMessage(password reset) failed: %s %s", r.status_code, r.text)
        r.raise_for_status()
