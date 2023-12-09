import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import json
from GptCore import GptGamemaster
import DbContext
import CharacterStateTracker
from CharacterStateEnum import CharacterStateEnum

with open("appsettings.json", "r") as settings:
    data = json.load(settings)

tgToken = data["Tokens"]["Telegram"]
gptKey = data["Tokens"]["ChatGPT"]

dbContext = DbContext.DbContext(**data["DbConnection"])

gamemaster = GptGamemaster(gptKey, dbContext)

characteristicToChange = ''

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def SendMessageWithButtons(update, context, message, buttons):
    if buttons == None: replyButtons = ReplyKeyboardRemove()
    elif not isinstance(buttons, (list,tuple)): replyButtons = ReplyKeyboardMarkup([buttons], one_time_keyboard=True, resize_keyboard=True)
    else: replyButtons = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

    await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=message,
    reply_markup=replyButtons
    )

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

async def StartWorldCreation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = 'Hello there, traveler! In what setting will your adventure go? You can choose one of the variants below, as well as type your own'
    buttons = [['Fantasy'], ['Future'], ['Sci-fi']]
    await SendMessageWithButtons(update, context, message, buttons)

async def CreateWorld(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    answer = gamemaster.CreateWorld(username,update.message.text)
    
    await SendMessageWithButtons(update, context, answer, None)
    await StartCharacterCreation(update, context)


async def StartCharacterCreation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = 'Great! We have created a world in which the campaign will be set in, now let\'s create your character. Tell me about yourself, you might want to mention your character\'s name, class, age, race, sex, and your incredibly tragic backstory. Although, what you want to mention is up to you'
    await SendMessageWithButtons(update, context, message, None)


def GetChangeCharacterButtons():
    return ['I like my character!'], ['Name', 'Class', 'Age'], ['Race', 'Sex', 'Backstory']


async def CreateCharacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    answer = gamemaster.CreateCharacter(username, update.message.text)
    message = 'Here is your character information. Do you like it, or would you like to change something?\n' + answer
    buttons = GetChangeCharacterButtons()
    await SendMessageWithButtons(update, context, message, buttons)


async def CreateStartingGearAndAbilities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    answer = gamemaster.CreateStaringGearAndAbilities(username)

    for message in answer:
        await SendMessageWithButtons(update, context, message, None)


async def StartChangingCharacterInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    characteristicToChange = update.message.text
    message = f'What would you like your character\'s new {characteristicToChange} to be?'
    await SendMessageWithButtons(update, context, message, None)


async def ChangeCharacterInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    newInfo = gamemaster.ChangeCharacterInfo(username, characteristicToChange, update.message.text)
    message = 'Would you like to change something else, or shall we begin?\n' + newInfo
    buttons = GetChangeCharacterButtons()
    await SendMessageWithButtons(update, context, message, buttons)

async def ButtonExpected(update, context, expectedButtons):
    message = 'Please, click one of the buttons provided to you'
    await SendMessageWithButtons(update, context, message, expectedButtons)

async def AssessCharacterCreation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    global characteristicToChange
    
    btn, secondRow, thirdRow = GetChangeCharacterButtons()
    changeButtons = [*secondRow, *thirdRow]
    match update.message.text:
        case 'I like my character!':
            CharacterStateTracker.SetCharacterState(dbContext, username, CharacterStateEnum.WaitingForCampaignStart)
            await CreateStartingGearAndAbilities(update, context)
        case x if x in changeButtons:
            CharacterStateTracker.SetCharacterState(dbContext, username, CharacterStateEnum.WaitingForCharacteristicChangeInput)
            characteristicToChange = update.message.text
            await StartChangingCharacterInfo(update, context)
        case _:
            await ButtonExpected(update, context, [btn, secondRow, thirdRow])


async def ChooseMethodBasedOnState(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    state = CharacterStateTracker.GetCharacterState(dbContext, username)
    match state:
        case x if x == None or x == CharacterStateEnum.CampaignEnded:
            CharacterStateTracker.SetCharacterState(dbContext, username, CharacterStateEnum.WaitingForWorldCreationInput)
            return await StartWorldCreation(update, context)
        case CharacterStateEnum.WaitingForWorldCreationInput:
            CharacterStateTracker.SetCharacterState(dbContext, username, CharacterStateEnum.WaitingForCharacterCreationInput)
            return await CreateWorld(update, context)
        case CharacterStateEnum.WaitingForCharacterCreationInput:
            CharacterStateTracker.SetCharacterState(dbContext, username, CharacterStateEnum.WaitingForCharacterCreationAssessment)
            return await CreateCharacter(update, context)
        case CharacterStateEnum.WaitingForCharacterCreationAssessment:
            CharacterStateTracker.SetCharacterState(dbContext, username, CharacterStateEnum.WaitingForCharacterCreationAssessment)
            return await AssessCharacterCreation(update, context)
        case CharacterStateEnum.WaitingForCharacteristicChangeInput:
            return await ChangeCharacterInfo(update, context)
         

if __name__ == '__main__':
    builder = ApplicationBuilder().connect_timeout(connect_timeout=15).read_timeout(read_timeout=15).write_timeout(write_timeout=15)
    application = builder.token(tgToken).build()
    
    msg_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, ChooseMethodBasedOnState)
    application.add_handler(msg_handler)

    application.run_polling()
    