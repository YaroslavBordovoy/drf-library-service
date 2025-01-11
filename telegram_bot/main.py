import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from rest_framework.generics import get_object_or_404
from telebot import TeleBot, types

from books_service.models import Book
from telegram_bot.redis_client import save_telegram_id, save_jwt_token, get_jwt_token
import requests


bot = TeleBot(os.getenv("TELEGRAM_TOKEN"))

API_BASE_URL = "http://library:8000/api"


# ======= Authorization =======


def is_authenticated(telegram_id):
    return get_jwt_token(telegram_id) is not None


def authenticate_user(email, password):
    response = requests.post(
        f"{API_BASE_URL}/users/token/", json={"email": email, "password": password}
    )

    if response.status_code == 200:
        return response.json()

    return None


@bot.message_handler(commands=["start"])
def main(message):
    """
    The /start command checks user authorization.
    """
    telegram_id = message.chat.id

    if is_authenticated(telegram_id):
        bot.send_message(telegram_id, "✅ You are already logged in!")
        show_menu(telegram_id)
    else:
        bot.send_message(telegram_id, "👋 Welcome! Please log in. Enter your email:")
        bot.register_next_step_handler(message, process_email)


def process_email(message):
    """
    Asks for a password after entering your email.
    """
    email = message.text.strip()
    bot.send_message(message.chat.id, "Enter your password:")
    bot.register_next_step_handler(message, process_password, email)


def process_password(message, email):
    """
    Authorizes the user via API.
    """
    password = message.text.strip()
    telegram_id = message.chat.id

    user_data = authenticate_user(email, password)

    if user_data:
        save_telegram_id(telegram_id, email)
        save_jwt_token(telegram_id, user_data["access"])  # Сохраняем JWT-токен
        bot.send_message(telegram_id, "Authorization successful! Welcome!")
        show_menu(telegram_id)

    else:
        bot.send_message(
            telegram_id, "Authorization error. Check your details and try again."
        )
        main(message)


# ======= Menu =======


def show_menu(telegram_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            "🔍 Search for a book", callback_data="get_book_info"
        ),
        types.InlineKeyboardButton("📚 My books", callback_data="my_books"),
    )
    bot.send_message(telegram_id, "Here's what I can do for you:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "menu")
def handle_menu(call):
    """
    Processing return to menu.
    """
    show_menu(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "get_book_info")
def handle_search_book(call):
    """
    Processing the "🔍 Search for a book" button.
    """
    msg = bot.send_message(
        call.message.chat.id, "Enter the title of the book to search:"
    )
    bot.register_next_step_handler(msg, process_book_search)


def search_book_by_title(title):
    """
    Search for a book via `title__icontains`.
    """
    from books_service.models import Book

    try:
        return Book.objects.get(title__icontains=title)
    except Book.DoesNotExist:
        return None


def process_book_search(message):
    title = message.text.strip()
    book = search_book_by_title(title)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 Back to menu", callback_data="menu"))

    if book:
        book_markup = types.InlineKeyboardMarkup()
        book_markup.add(
            types.InlineKeyboardButton("📖 Book now", callback_data=f"book_{book.id}")
        )
        bot.send_message(
            message.chat.id,
            f"Title: {book.title}\nAuthor: {book.author}\n"
            f"In stock: {book.inventory}\n"
            f"Daily price: {book.daily_fee}",
            reply_markup=book_markup,
        )
    else:
        msg = bot.send_message(
            message.chat.id, "Book not found. Try again:", reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_book_search)


@bot.callback_query_handler(func=lambda call: call.data == "my_books")
def handle_my_books(call):
    """
    Processing the "📚 My books" button.
    """
    telegram_id = call.message.chat.id
    jwt_token = get_jwt_token(telegram_id)

    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{API_BASE_URL}/booking/borrowings/", headers=headers)

    if response.status_code == 200 and response.json():
        borrowings = response.json()
        for borrowing in borrowings:
            bot.send_message(
                call.message.chat.id,
                f"Book: {borrowing["book"]["title"]}\n"
                f"Booking Date: {borrowing["borrow_date"]}\n"
                f"Expected Return Date: {borrowing["expected_return_date"]}\n",
            )
    else:
        bot.send_message(call.message.chat.id, "You have no active bookings.")


# ======= Booking a book =======


@bot.callback_query_handler(func=lambda call: call.data.startswith("book_"))
def handle_booking(call):
    """
    Book Reservations Beginning
    """
    book_id = int(call.data.split("_")[1])
    msg = bot.send_message(
        call.message.chat.id, "Please enter the book return date (YYYY-MM-DD):"
    )
    bot.register_next_step_handler(msg, process_booking_date, book_id)


def book_a_book(telegram_id, book_id, expected_return_date):
    """
    Sends a request to reserve a book via the API.
    """
    jwt_token = get_jwt_token(telegram_id)
    headers = {"Authorization": f"Bearer {jwt_token}"}

    data = {"book": str(book_id), "expected_return_date": expected_return_date}

    print("Request Headers:", headers)
    print("Request Data:", data)

    try:
        response = requests.post(
            f"{API_BASE_URL}/booking/borrowings/", json=data, headers=headers
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        bot.send_message(telegram_id, f"Error during booking: {e}")
        return None

    print("Response Status Code:", response.status_code)
    print("Response Body:", response.text)

    return response


def process_booking_date(message, book_id):
    """
    Processes the return date and reserves the book.
    """
    try:
        expected_return_date = message.text.strip()
        telegram_id = message.chat.id

        response = book_a_book(telegram_id, book_id, expected_return_date)

        if response.status_code == 201:
            book = get_object_or_404(Book, pk=book_id)

            message = (
                f"💳 Pay for the book reservation: {book.title}.\n"
                f"To pay, follow the link: {response.json()['payments'][0]['session_url']}\n"
                "Thank you for using our library!"
            )

            bot.send_message(telegram_id, "Booking successful!")
            bot.send_message(telegram_id, message)

        else:
            bot.send_message(telegram_id, f"Booking failed: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Booking Error: {e}")


# ======= notifications =======


def send_notification(telegram_id, message):
    """
    Sends a notification via Telegram.
    """
    bot.send_message(telegram_id, message)


if __name__ == "__main__":
    print("The bot has been launched...")
    bot.polling()
