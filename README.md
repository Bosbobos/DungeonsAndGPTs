***Telegram DND Bot - Dungeon Mastered by ChatGPT***
Welcome to the Telegram DND Bot repository, where the magical world of Dungeons and Dragons comes to life through the enchanting storytelling prowess of ChatGPT. Transform your Telegram group into an immersive DND campaign with this interactive and engaging bot.

**Features**
*Dynamic Storytelling:* Enjoy a rich and evolving narrative crafted by ChatGPT, the Dungeon Master extraordinaire. Every decision and action you take shapes the unfolding tale.

*Character Creation:* Dive into the world of fantasy by creating your own unique character. Define your race, class, and background to embark on a heroic journey.

*Quests and Adventures:* Embark on epic quests and face challenging adventures. Encounter mythical creatures, solve puzzles, and make choices that impact the course of the story.

*Interactive Combat:* Engage in thrilling battles with monsters and foes. Utilize your character's abilities and make strategic decisions in combat scenarios.

*Different settings:* Do you like classic medieval fantasy, or would you rather embark on a futuristic sci-fi journey? Don't worry, we've got you covered! You can choose abolutely any setting you want.

**Getting Started**
*Prerequisites*
Telegram account
Token from the BotFather to set up the Telegram bot
API token from ChatGPT 
**Installation**
Clone this repository to your local machine:

```
git clone https://github.com/your-username/telegram-dnd-bot.git
```
Install the required dependencies:

```
pip install -r requirements.txt
```
Set up your Telegram bot using the BotFather on Telegram. Obtain the token.

Create a file named appsettings.json in the project root and add your Telegram bot token and ChatGPT api token, as well a DB connection string:

``` json
{
    "Tokens": {
        "Telegram": "",
        "ChatGPT": ""
    },
    "DbConnection": {
        "dbname": "",
        "user": "",
        "password": "",
        "host": "",
        "port": ""
    }
}
```
Run the bot:

```
python TelegramBot.py
```
Type /start to the bot and embark on a new adventure!

Alternatively, you can just write the bot on @dungeonsandgptstest_bot
