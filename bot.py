import os
from dotenv import load_dotenv
import telebot
from image_generate import text_to_image

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "bol")



@bot.message_handler()
def bot_handler(message):
    text = message.text
    response = text_to_image(text)
    photo = open(response["image_path"], 'rb')
    sent_msg = bot.send_photo(
        message.chat.id, photo)


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()