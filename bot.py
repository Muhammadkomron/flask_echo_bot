import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, abort
import telebot
from telebot import types

# Load environment variables
load_dotenv()

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'default-secret')
MAX_CONNECTIONS = os.getenv('MAX_CONNECTIONS', 5)
PORT = int(os.getenv('PORT', 8000))

# Validate required variables
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is required!")
    exit(1)

if not WEBHOOK_URL:
    logger.error("WEBHOOK_URL is required!")
    exit(1)

logger.info(f"Starting bot with token: {BOT_TOKEN[:10]}...")
logger.info(f"Webhook URL: {WEBHOOK_URL}")

# Initialize bot and Flask app
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


# Set webhook
def setup_webhook():
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook/"
        logger.info(f"Setting webhook to: {webhook_url}")

        # Remove old webhook first
        bot.remove_webhook()

        # Set new webhook
        result = bot.set_webhook(
            url=webhook_url,
            secret_token=SECRET_TOKEN,
            max_connections=MAX_CONNECTIONS,
        )

        if result:
            logger.info("✅ Webhook set successfully")
        else:
            logger.error("❌ Failed to set webhook")

    except Exception as e:
        logger.error(f"Error setting webhook: {e}")


# Setup webhook on startup
setup_webhook()


@app.route('/webhook/', methods=['POST'])
def webhook():
    """Handle incoming webhook requests"""
    try:
        # Check secret token
        received_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if received_token != SECRET_TOKEN:
            logger.warning(f"Invalid token: {received_token}")
            abort(403)

        # Process the update
        json_string = request.get_data(as_text=True)
        logger.info(f"Received update: {json_string[:100]}...")

        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])

        return '', 200

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        abort(500)


@app.route('/health/')
def health():
    """Simple health check"""
    try:
        bot_info = bot.get_me()
        return {
            'status': 'ok',
            'bot_username': bot_info.username
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'error', 'message': str(e)}, 500


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    """Handle /start and /help commands"""
    logger.info(f"Start command from user {message.from_user.id}")

    welcome_text = """
🤖 Hello! I'm a simple echo bot.

Send me any text message and I'll echo it back to you.

Commands:
/start - Show this message
/help - Show this message
    """

    bot.reply_to(message, welcome_text)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handle text messages - simple echo"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        text = message.text

        logger.info(f"Message from {username} ({user_id}): {text}")

        # Simple echo response
        response = f"You said: {text}"

        bot.reply_to(message, response)
        logger.info("✅ Response sent")

    except Exception as e:
        logger.error(f"Error handling text: {e}")
        bot.reply_to(message, "Sorry, something went wrong!")


@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def handle_media(message):
    """Handle media messages"""
    content_type = message.content_type
    logger.info(f"Received {content_type} from user {message.from_user.id}")

    bot.reply_to(message, f"I received your {content_type}! But I only echo text messages. 📝")


if __name__ == '__main__':
    logger.info("🚀 Starting Telegram Echo Bot...")
    logger.info(f"Bot username: @{bot.get_me().username}")
    logger.info(f"Running on port {PORT}")

    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False
    )
