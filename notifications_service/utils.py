from telegram.ext import Application
import os

application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

async def send_telegram_message(telegram_id, message):
    """
    Sends a message to the user via Telegram.
    :param telegram_id: The user's Telegram ID.
    :param message: The message text.
    """
    try:
        await application.bot.send_message(chat_id=telegram_id, text=message)
        print(f"Message sent to user {telegram_id}.")
    except Exception as e:
        print(f"Error sending message to user {telegram_id}: {e}")
