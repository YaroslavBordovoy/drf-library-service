from borrowing_service.models import Borrowing
from payments_service.models import Payment
from telegram_bot.redis_client import get_telegram_id


def notify_booking_created(instance: Borrowing):
    """
    Notification of successful booking
    """
    telegram_id = get_telegram_id(instance.user.email)

    if not telegram_id:
        print(f"Telegram ID for user {instance.user.email} not found in Redis.")
        return

    message = (
        f"📚 You have successfully booked the book: {instance.book.title}\n"
        f"Booking date: {instance.borrow_date}\n"
        f"Expected return date: {instance.expected_return_date}.\n"
        "Enjoy reading!"
    )
    print(f"Telegram id in notifications: {telegram_id}")

    return telegram_id, message


def notify_payment_needed(instance: Payment):
    """
    Notification of payment required.
    """
    telegram_id = get_telegram_id(instance.borrowing.user.email)

    if not telegram_id:
        print(f"Telegram ID for user {instance.borrowing.user.email} not found in Redis.")
        return

    message = (
        f"💳 Pay for the book reservation: {instance.borrowing.book.title}.\n"
        f"To pay, follow the link: {instance.session_url}\n"
        "Thank you for using our library!"
    )

    return telegram_id, message
