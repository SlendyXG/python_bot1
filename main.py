import asyncio
import os
import time

import requests
import telegram
from dotenv import load_dotenv


def get_last_timestamp(token):
    url = "https://dvmn.org/api/user_reviews"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    if not data["results"]:
        return time.time()
    return max(r["timestamp"] for r in data["results"])


def format_attempt(attempt):
    if attempt["is_negative"]:
        status = "Работа не принята"
    else:
        status = "Работа принята"

    title = attempt["lesson_title"] or "Без названия"
    url = attempt.get("lesson_url", "")

    text = f"Преподаватель проверил работу!\n\n{status}\n\n{title}"
    if url:
        text += f"\n{url}"
    return text


async def notify(bot, chat_id, data):
    for attempt in data["new_attempts"]:
        await bot.send_message(
            chat_id=chat_id,
            text=format_attempt(attempt),
            disable_web_page_preview=True,
        )


async def long_poll(token, bot, chat_id, last_timestamp):
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {token}"}

    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                params={"timestamp": last_timestamp},
                timeout=(10, 90),
            )
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения: {e}")
            time.sleep(5)
            continue

        data = response.json()

        if data["status"] == "timeout":
            continue

        if data["status"] == "found":
            await notify(bot, chat_id, data)
            last_timestamp = max(
                data["last_attempt_timestamp"],
                max(a["timestamp"] for a in data["new_attempts"]),
            )


async def main():
    load_dotenv()
    token = os.environ["DEVMAN_TOKEN"]
    bot = telegram.Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    last_timestamp = get_last_timestamp(token)

    await long_poll(token, bot, chat_id, last_timestamp)


if __name__ == "__main__":
    asyncio.run(main())