from notifications_service.utils import send_telegram_message
from telegram_bot.redis_client import get_telegram_id


async def notify_booking_created(user_id, book_title, borrow_date, expected_return_date):
    """
    Notification of successful booking
    """
    telegram_id = get_telegram_id(user_id)

    if not telegram_id:
        print(f"Telegram ID for user {user_id} not found in Redis.")
        return

    message = (
        f"📚 You have successfully booked the book: {book_title}\n"
        f"Booking date: {borrow_date}\n"
        f"Expected return date: {expected_return_date}.\n"
        "Enjoy reading!"
    )

    await send_telegram_message(telegram_id, message)


async def notify_payment_needed(user_id, book_title, payment_url):
    """
    Notification of payment required.
    """
    telegram_id = get_telegram_id(user_id)

    if not telegram_id:
        print(f"Telegram ID for user {user_id} not found in Redis.")
        return

    message = (
        f"💳 Pay for the book reservation: {book_title}.\n"
        f"To pay, follow the link: {payment_url}\n"
        "Thank you for using our library!"
    )

    await send_telegram_message(telegram_id, message)