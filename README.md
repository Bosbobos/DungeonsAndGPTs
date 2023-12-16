# Telegram DND Bot - Dungeon Mastered by ChatGPT

Welcome to the Telegram DND Bot repository, where the magical world of Dungeons and Dragons comes to life through the enchanting storytelling prowess of ChatGPT. Transform your Telegram group into an immersive DND campaign with this interactive and engaging bot.

## Features

- **Dynamic Storytelling**: Enjoy a rich and evolving narrative crafted by ChatGPT, the Dungeon Master extraordinaire. Every decision and action you take shapes the unfolding tale.

- **Character Creation**: Dive into the world of fantasy by creating your own unique character. Define your race, class, and background to embark on a heroic journey.

- **Quests and Adventures**: Embark on epic quests and face challenging adventures. Encounter mythical creatures, solve puzzles, and make choices that impact the course of the story.

- **Interactive Combat**: Engage in thrilling battles with monsters and foes. Utilize your character's abilities and make strategic decisions in combat scenarios.

- **Different Settings**: Choose between classic medieval fantasy or a futuristic sci-fi journey. The bot supports a variety of settings to suit your preferences.

## Getting Started

### Prerequisites

- Telegram account
- Token from the BotFather to set up the Telegram bot
- API token from ChatGPT

### Installation

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/your-username/telegram-dnd-bot.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your Telegram bot using the BotFather on Telegram. Obtain the token.

4. Create a file named `appsettings.json` in the project root and add your Telegram bot token, ChatGPT API token, and DB connection string:

    ```json
    {
        "Tokens": {
            "Telegram": "your-telegram-bot-token",
            "ChatGPT": "your-chatgpt-api-token"
        },
        "DbConnection": {
            "dbname": "your-db-name",
            "user": "your-db-user",
            "password": "your-db-password",
            "host": "your-db-host",
            "port": "your-db-port"
        }
    }
    ```

5. Run the bot:

    ```bash
    python TelegramBot.py
    ```

6. Type `/start` to the bot and embark on a new adventure!

Alternatively, you can interact with the bot directly on [@dungeonsandgptstest_bot](https://t.me/dungeonsandgptstest_bot).

Happy adventuring!
