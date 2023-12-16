import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


async def SendMessageWithButtons(update, context, message, buttons):
    if buttons == None:
        replyButtons = ReplyKeyboardRemove()
    elif isinstance(buttons, dict):
        replyButtons = list(buttons.values)
    elif not isinstance(buttons, (list, tuple)):
        replyButtons = ReplyKeyboardMarkup(
            [[buttons]], one_time_keyboard=True, resize_keyboard=True)
    else:
        replyButtons = ReplyKeyboardMarkup(
            buttons, one_time_keyboard=True, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=replyButtons
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm alive!")


async def SendGptMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = gamemaster.SendMessage('', 'Hello!', 0)
    await update.message.reply_text(answer)


async def StartWorldCreation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['FinalBattle'] = 'Ahead'
    message = 'Hello there, traveler! In what setting will your adventure go? You can choose one of the variants below, as well as type your own'
    buttons = [['Fantasy'], ['Future'], ['Sci-fi']]
    await SendMessageWithButtons(update, context, message, buttons)


async def CreateWorld(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    answer = gamemaster.CreateWorld(username, update.message.text)

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

    gear, abilities = answer

    gearString = 'Wait, did your character always have these items? Nevermind, now they do\n'
    for pieceOfGear in gear:
        gearString += pieceOfGear

    abilitiesString = 'Look at how many abilities your character has! They\'re definetly going to achieve a lot with such knowledge\n'
    for skill in abilities:
        abilitiesString += skill

    abilitiesString = abilitiesString.replace(
        'BeautifulDescription', 'Description')
    await SendMessageWithButtons(update, context, gearString, None)
    await SendMessageWithButtons(update, context, abilitiesString, None)

    message = 'Are your ready to begin your campaign?'
    button = 'Let\'s start!'
    await SendMessageWithButtons(update, context, message, button)


async def StartChangingCharacterInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    characteristicToChange = update.message.text
    context.user_data['characteristicToChange'] = characteristicToChange
    message = f'What would you like your character\'s new {
        characteristicToChange.lower()} to be?'
    await SendMessageWithButtons(update, context, message, None)


async def ChangeCharacterInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    newInfo = gamemaster.ChangeCharacterInfo(
        username, context.user_data['characteristicToChange'], update.message.text)
    message = 'Would you like to change something else, or shall we begin?\n' + newInfo
    buttons = GetChangeCharacterButtons()
    await SendMessageWithButtons(update, context, message, buttons)


async def ButtonExpected(update, context, expectedButtons):
    message = 'Please, click one of the buttons provided to you'
    await SendMessageWithButtons(update, context, message, expectedButtons)


async def AssessCharacterCreation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']

    btn, secondRow, thirdRow = GetChangeCharacterButtons()
    changeButtons = [*secondRow, *thirdRow]
    match update.message.text:
        case 'I like my character!':
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.WaitingForCampaignStart)
            await CreateStartingGearAndAbilities(update, context)
        case x if x in changeButtons:
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.WaitingForCharacteristicChangeInput)
            context.user_data['characteristicToChange'] = update.message.text
            await StartChangingCharacterInfo(update, context)
        case _:
            await ButtonExpected(update, context, [btn, secondRow, thirdRow])


async def StartCampaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    text, actions = gamemaster.StartCampaign(username)

    actionsList = []
    for action in actions:
        actionsList.append([action])

    context.user_data['possibleActions'] = actionsList

    await SendMessageWithButtons(update, context, text, actionsList)


async def MakeExplorationPlayerTurn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    msg = update.message.text
    try:
        possible = context.user_data['possibleActions']
    except KeyError:
        possible = dbContext.read_latest_record(
            'character_state', 'username', username)['possible_actions']
    if not all(isinstance(button, list) for button in possible):
        possibleButtons = [[x] for x in possible]
    else:
        possibleButtons = possible

    if msg not in possible and [msg] not in possible and not any(msg.rstrip('...').rstrip('…') in x for x in possible):
        await SendMessageWithButtons(update, context, 'You can\'t do that in the current situation! Please, choose one of the provided options', possibleButtons)
        return

    text, actions = gamemaster.MakeExplorationPlayerTurn(username, msg)

    actionsList = []
    for action in actions:
        actionsList.append([action])

    context.user_data['possibleActions'] = actionsList

    await SendMessageWithButtons(update, context, text, actionsList)

    try:
        if context.user_data['FinalBattle'] == 'Started':
            return await FinishTheCampaign(update, context)
    except KeyError:
        pass


async def StartFinalBattle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    msg = update.message.text
    try:
        possible = context.user_data['possibleActions']
    except KeyError:
        possible = dbContext.read_latest_record(
            'character_state', 'username', username)['possible_actions']
    possibleButtons = [[x] for x in possible]

    if msg not in possible and [msg] not in possible and not any(msg.rstrip('...').rstrip('…') in x for x in possible):
        await SendMessageWithButtons(update, context, 'You can\'t do that in the current situation! Please, choose one of the provided options', possibleButtons)
        return

    context.user_data['FinalBattle'] = 'Started'
    text, actions = gamemaster.StartFinalFight(username, msg)

    actionsList = []
    for action in actions:
        actionsList.append([action])

    context.user_data['possibleActions'] = actionsList

    await SendMessageWithButtons(update, context, text, actionsList)


async def FinishTheCampaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']

    message, actions = gamemaster.FinishTheCampaign(username)
    CharacterStateTracker.SetCharacterState(
        dbContext, username, CharacterStateEnum.CampaignEnded)

    context.user_data['FinalBattle'] = 'Ended'

    await SendMessageWithButtons(update, context, message, [['To the new adventures!']])


async def ChooseMethodBasedOnState(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user['username']
    state = CharacterStateTracker.GetCharacterState(dbContext, username)

    turns = dbContext.read_latest_record(
        'character_state', 'username', username)['turn']
    if turns >= 10:
        try:
            if context.user_data['FinalBattle'] == 'Started' and state == CharacterStateEnum.Exploring:
                return await FinishTheCampaign(update, context)
        except KeyError:
            context.user_data['FinalBattle'] = 'Started'
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.InFinalBattle)
            return await StartFinalBattle(update, context)
    match state:
        case x if x == None or x == CharacterStateEnum.CampaignEnded:
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.WaitingForWorldCreationInput)
            return await StartWorldCreation(update, context)
        case CharacterStateEnum.WaitingForWorldCreationInput:
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.WaitingForCharacterCreationInput)
            return await CreateWorld(update, context)
        case CharacterStateEnum.WaitingForCharacterCreationInput:
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.WaitingForCharacterCreationAssessment)
            return await CreateCharacter(update, context)
        case CharacterStateEnum.WaitingForCharacterCreationAssessment:
            return await AssessCharacterCreation(update, context)
        case CharacterStateEnum.WaitingForCharacteristicChangeInput:
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.WaitingForCharacterCreationAssessment)
            return await ChangeCharacterInfo(update, context)
        case CharacterStateEnum.WaitingForCampaignStart:
            CharacterStateTracker.SetCharacterState(
                dbContext, username, CharacterStateEnum.Exploring)
            return await StartCampaign(update, context)
        case CharacterStateEnum.Exploring:
            try:
                if context.user_data['FinalBattle'] == 'Started':
                    return await FinishTheCampaign(update, context)
                elif context.user_data['FinalBattle'] == 'Ended':
                    return await StartWorldCreation(update, context)
                else:
                    return await MakeExplorationPlayerTurn(update, context)
            except KeyError:
                return await MakeExplorationPlayerTurn(update, context)
        case CharacterStateEnum.InBattle:
            return await MakeExplorationPlayerTurn(update, context)
        case CharacterStateEnum.InFinalBattle:
            return await MakeExplorationPlayerTurn(update, context)
        case _:
            return await SendMessageWithButtons(update, context, f'Unknown state: {state}', None)


if __name__ == '__main__':
    builder = ApplicationBuilder().connect_timeout(connect_timeout=15).read_timeout(
        read_timeout=15).write_timeout(write_timeout=15)
    application = builder.token(tgToken).build()

    msg_handler = MessageHandler(
        filters.TEXT & ~filters.COMMAND, ChooseMethodBasedOnState)
    application.add_handler(msg_handler)

    application.run_polling()
