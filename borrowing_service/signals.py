from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing_service.models import Borrowing
from notifications_service.notifications import notify_booking_created


@receiver([post_save], sender=Borrowing)
def handle_borrowing_created(sender, instance, **kwargs):
    print(f"instance borrowing: {instance}")
    from telegram_bot.main import send_notification
    telegram_id, message = notify_booking_created(instance)
    send_notification(telegram_id, message)

