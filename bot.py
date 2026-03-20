import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client safely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        groq_client = None
else:
    logger.warning("GROQ_API_KEY not set; Telegram bot AI features disabled.")
    groq_client = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm the Tenex Tutorials Assistant. 🎓 Ask me any doubt about Class 10 Math or Science!",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Just send me a message with your question, and I'll use AI to help you solve it!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message and get a response from Groq."""
    user_msg = update.message.text

    if not groq_client:
        await update.message.reply_text("AI service is not configured. Please contact the administrator.")
        return

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful math and science tutor for Indian Class 10 students (CBSE/ICSE). Keep answers concise and tutorial-like."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=300,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        logger.error(f"Groq Error: {e}")
        await update.message.reply_text("Sorry, I'm having trouble thinking right now. Please try again later!")

def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not found. Bot will not start.")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Telegram Bot logic initialized. Polling disabled for Railway integration demo.")

if __name__ == "__main__":
    main()
