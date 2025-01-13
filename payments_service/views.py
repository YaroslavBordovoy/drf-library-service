import os

import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from telegram_bot.main import send_notification
from telegram_bot.redis_client import get_telegram_id
from borrowing_service.models import Borrowing


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@api_view(["GET"])
def payment_success(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, id=borrowing_id)
    book = borrowing.book
    email = borrowing.user.email

    telegram_id = get_telegram_id(email)

    if not telegram_id:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unable to find Telegram ID of user.",
            }
        )

    message = (
        f"📚 You have successfully booked the book: {book.title}\n"
        f"Booking date: {borrowing.borrow_date}\n"
        f"Expected return date: {borrowing.expected_return_date}.\n"
        f"Thank you for your payment! Enjoy reading! 😊"
    )

    send_notification(telegram_id, message)

    return JsonResponse(
        {"status": "success", "message": "Booking successfully completed!"}
    )
