import io
import logging
import os

import telebot
from dotenv import load_dotenv

from image_generate import text_to_image

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(message, "bol")


@bot.message_handler(content_types=["text"])
def bot_handler(message):
    try:
        png = text_to_image(
            message.text,
            display_name=os.getenv("IMAGE_DISPLAY_NAME"),
            username=os.getenv("IMAGE_USERNAME"),
            timestamp=message.date,
        )
        # bot.send_photo(message.chat.id, io.BytesIO(png))
        # Telegram recompresses photos (max ~2560px); document keeps full 2160x4680
        doc = io.BytesIO(png)
        doc.name = "card.png"
        bot.send_document(message.chat.id, doc)
    except Exception:
        logging.exception("failed to render message from chat %s", message.chat.id)
        bot.reply_to(message, "couldn't render that one, try again")


if __name__ == "__main__":
    bot.infinity_polling()
