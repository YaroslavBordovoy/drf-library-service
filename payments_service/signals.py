from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications_service.notifications import notify_payment_needed
from payments_service.models import Payment


@receiver([post_save], sender=Payment)
def handle_payment_created(sender, instance, **kwargs):
    print(f"instance payment: {instance}")
    from telegram_bot.main import send_notification
    if instance.session_url:
        telegram_id, message = notify_payment_needed(instance)
        send_notification(telegram_id, message)
