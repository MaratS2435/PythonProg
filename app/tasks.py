from celery import Celery
import telebot

from app.config import TELEGRAM_BOT_TOKEN, BROKER_URL

celery_app = Celery("tasks", broker=BROKER_URL, backend='rpc://')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@celery_app.task
def send_telegram_message(chat_id: int, message: str):
    bot.send_message(chat_id=chat_id, text=message)