import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import json
from GptCore import GptGamemaster
import DbContext

with open("appsettings.json", "r") as settings:
    data = json.load(settings)

tgToken = data["Tokens"]["Telegram"]
gptKey = data["Tokens"]["ChatGPT"]

dbContext = DbContext.DbContext(**data["DbConnection"])

gamemaster = GptGamemaster(gptKey, dbContext)

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

async def SendGptMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = gamemaster.SendMessage('', 'Hello!', 0)
    await update.message.reply_text(answer)

async def CreateWorld(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    answer = gamemaster.CreateWorld(username,update.message.text)
    
    await update.message.reply_text(answer)

async def CreateCharacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.message.from_user['username']
        answer = gamemaster.CreateCharacter(username, update.message.text)

        await update.message.reply_text(answer)

if __name__ == '__main__':
    builder = ApplicationBuilder().connect_timeout(connect_timeout=15).read_timeout(read_timeout=15).write_timeout(write_timeout=15)
    application = builder.token(tgToken).build()
    
    start_handler = CommandHandler('start', start)
    gpt_msg_sender = MessageHandler(filters.Regex('SendMessage'), SendGptMessage)
    world_creator = MessageHandler(filters.Regex('Fantasy'), CreateWorld)
    character_creator = MessageHandler(filters.Regex('I\'m Hwei, a brooding painter who creates brilliant art in order to confront Ionia\'s criminals and comfort their victims'), CreateCharacter)
    msg_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    application.add_handler(start_handler)
    application.add_handler(gpt_msg_sender)
    application.add_handler(world_creator)
    application.add_handler(character_creator)
    application.add_handler(msg_handler)

    application.run_polling()
    