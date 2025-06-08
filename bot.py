import os
import logging

from dotenv import load_dotenv
from flask import Flask, request, abort
import telebot
from telebot import types

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')

# Initialize
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)


# Bot handlers
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.reply_to(message, "🤖 Hello! Send me any text and I'll echo it back!")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    logger.info(f"Text from {message.from_user.id}: {message.text}")
    bot.reply_to(message, f"You said: {message.text}")


# Flask routes
@app.route('/webhook/', methods=['POST'])
def webhook():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != SECRET_TOKEN:
        abort(403)

    update = types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return '', 200


@app.route('/health/')
def health():
    return {'status': 'healthy', 'bot': bot.get_me().username}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
