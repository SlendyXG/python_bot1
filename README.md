# Devman checking bot

The program monitors Devman for checked works and sends Telegram notifications when a work is reviewed.

## How to install

### Obtaining API Keys

The program requires the following keys to function:

#### Devman API Token
1. Log in to [dvmn.org](https://dvmn.org/)
2. Open your profile settings and find the API section
3. Copy your personal API token

#### Telegram Bot Token
1. Message @BotFather on Telegram
2. Send the `/newbot` command and follow the instructions
3. Get your bot token (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Telegram Chat ID
1. Send `/start` to your bot from your personal Telegram account
2. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
3. Find the `"chat": {"id": ...}` value in the response — this is your Chat ID (a number, not a `@username`)

Create a `.env` file and add your tokens and chat ID. Here's an example:

```
DEVMAN_TOKEN=[Devman API token]
TELEGRAM_BOT_TOKEN=[Bot's token]
TELEGRAM_CHAT_ID=[Your numeric Telegram chat ID]
```

Python3 should be already installed.
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:

```
pip install -r requirements.txt
```

## Launch

### Scripts Usage Examples

#### Start monitoring checked works

```
#Start the bot that watches Devman for reviewed works and notifies via Telegram
python main.py
```

After launching, the script prints the starting `timestamp` and enters long polling. When a work is reviewed, a message arrives in Telegram:

```
Преподаватель проверил работу!

Работа принята

Верстаем видеоплеер
https://dvmn.org/modules/django-layout/lesson/player-layout/
```

The bot keeps running and sends a new notification for each checked work. Stop it with `Ctrl+C`.
## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
