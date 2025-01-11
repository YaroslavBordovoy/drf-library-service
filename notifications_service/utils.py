from dotenv import load_dotenv
from telegram.ext import Application
import os

load_dotenv()

application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()


async def send_telegram_message(telegram_id, message):
    """
    Sends a message to the user via Telegram.
    :param telegram_id: The user's Telegram ID.
    :param message: The message text.
    """
    try:
        await application.bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        raise RuntimeError (f"Error sending message to user {telegram_id}: {e}")
