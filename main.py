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
    reviews = response.json()
    if not reviews["results"]:
        return time.time()
    return max(review["timestamp"] for review in reviews["results"])


def format_attempt(attempt):
    if attempt["is_negative"]:
        status = "Работа не принята"
    else:
        status = "Работа принята"

    title = attempt["lesson_title"] or "Без названия"
    url = attempt.get("lesson_url", "")

    if url:
        return (
            f"Преподаватель проверил работу!\n\n"
            f"{status}\n\n"
            f"{title}\n"
            f"{url}"
        )

    return (
        f"Преподаватель проверил работу!\n\n"
        f"{status}\n\n"
        f"{title}"
    )


async def notify(bot, chat_id, event):
    for attempt in event["new_attempts"]:
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

        event = response.json()

        if event["status"] == "timeout":
            continue

        if event["status"] == "found":
            await notify(bot, chat_id, event)
            last_timestamp = max(
                event["last_attempt_timestamp"],
                max(attempt["timestamp"] for attempt in event["new_attempts"]),
            )


async def main():
    load_dotenv()
    token = os.environ["DEVMAN_TOKEN"]
    bot = telegram.Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    last_timestamp = get_last_timestamp(token)
    print(f"Стартуем с timestamp = {last_timestamp}")

    await long_poll(token, bot, chat_id, last_timestamp)


if __name__ == "__main__":
    asyncio.run(main())
