import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import json

with open("appsettings.json", "r") as settings:
    data = json.load(settings)

tgToken = data["Tokens"]["Telegram"]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm alive!")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Пойти налево"], ["Пойти направо"], ["Улететь на ракете"]]
    await update.message.reply_text(
        "Перед собой ты видишь развилку, куда ты направишься?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )

if __name__ == '__main__':
    builder = ApplicationBuilder().connect_timeout(connect_timeout=10).read_timeout(read_timeout=10).write_timeout(write_timeout=10)
    application = builder.token(tgToken).build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    application.run_polling()