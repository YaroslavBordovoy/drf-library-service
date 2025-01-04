import os
from datetime import datetime

import psycopg2
from telebot import types
from django.db.models.signals import post_save
from django.dispatch import receiver
from telebot import TeleBot

from books_service.models import Book
from borrowing_service.models import Borrowing


bot = TeleBot(os.getenv("TELEGRAM_TOKEN"))


def connect_to_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
    return conn


@bot.message_handler(commands=["start"])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔍 Search for a book", callback_data='get_book_info'),
        types.InlineKeyboardButton("📚 My books", callback_data='edit'),
        types.InlineKeyboardButton("📖 Book a book", callback_data='edit')
    )
    markup.row(
        types.InlineKeyboardButton("✏️ registration", callback_data='edit'),
        types.InlineKeyboardButton("👥 login", callback_data='edit')
    )
    bot.send_message(
        message.chat.id,
        "Hi, I'm a library bot 📚. I can help you with finding books and making reservations.\n"
        "Here's what I can do:",
        reply_markup=markup
    )


def search_book_by_title(title):
    try:
        return Book.objects.get(title__icontains=title)
    except Book.DoesNotExist:
        return None


@bot.callback_query_handler(func=lambda call: call.data == 'get_book_info')
def handle_get_book_info(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the title of the book you're looking for:")
    bot.register_next_step_handler(msg, process_book_search)


def process_book_search(message):
    title = message.text.strip()
    book = search_book_by_title(title)

    if book:
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📖 Book this book", callback_data=f'book_{book.id}'),
            types.InlineKeyboardButton("🚫 Not this time", callback_data='start_again')
        )
        bot.send_message(
            message.chat.id,
            f"Book found: {book.title}\n"
            f"Author: {book.author}\n"
            f"Cover: {book.cover}\n"
            f"Daily fee: {book.daily_fee}\n"
            f"Inventory: {book.inventory}",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "Sorry, we couldn't find a book with that title. Please try again.")
        main(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('book_'))
def handle_booking(call):
    book_id = int(call.data.split('_')[1])
    book = Book.objects.get(id=book_id)

    msg = bot.send_message(call.message.chat.id, f"Please enter the expected return date for the book '{book.title}' (YYYY-MM-DD):")
    bot.register_next_step_handler(msg, process_book_booking, book)


def process_book_booking(message, book):
    expected_return_date = message.text.strip()

    try:
        expected_return_date = datetime.strptime(expected_return_date, '%Y-%m-%d').date()

        borrowing = Borrowing.objects.create(
            user=message.from_user,
            book=book,
            expected_return_date=expected_return_date
        )
        send_notification(message.from_user.id, book.title, borrowing.borrow_date)

        bot.send_message(message.chat.id, f"You've successfully reserved the book '{book.title}' until {expected_return_date}.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid date format! Please try again.")
        process_book_booking(message, book)


@bot.callback_query_handler(func=lambda call: call.data == 'start_again')
def start_again(call):
    main(call.message)


def send_notification(user_id, book_title, borrow_date):
    message = f"Привіт! Ви успішно забронювали книгу: {book_title}. Дата бронювання: {borrow_date}."
    bot.send_message(user_id, message)


@receiver(post_save, sender=Borrowing)
def notify_user_on_borrowing(sender, instance, created, **kwargs):
    if created:
        user_id = instance.user.id
        book_title = instance.book.title
        borrow_date = instance.borrow_date
        send_notification(user_id, book_title, borrow_date)


bot.polling()
