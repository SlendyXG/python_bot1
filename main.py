import asyncio
import logging
import os
import time

import aiohttp
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


async def get_last_timestamp(session, token):
    url = "https://dvmn.org/api/user_reviews"
    headers = {"Authorization": f"Token {token}"}
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        reviews = await response.json()
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


async def long_poll(session, token, bot, chat_id, last_timestamp):
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {token}"}

    while True:
        try:
            async with session.get(
                url,
                headers=headers,
                params={"timestamp": last_timestamp},
                timeout=aiohttp.ClientTimeout(total=None, sock_read=90, sock_connect=10),
            ) as response:
                response.raise_for_status()
                event = await response.json()
        except asyncio.TimeoutError:
            continue
        except aiohttp.ClientConnectionError:
            logger.warning("Нет соединения, повторяю через 5 секунд")
            await asyncio.sleep(5)
            continue

        if event["status"] == "timeout":
            continue

        if event["status"] == "found":
            await notify(bot, chat_id, event)
            last_timestamp = max(
                event["last_attempt_timestamp"],
                max(attempt["timestamp"] for attempt in event["new_attempts"]),
            )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    load_dotenv()
    token = os.environ["DEVMAN_TOKEN"]
    bot = telegram.Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    async with aiohttp.ClientSession() as session:
        last_timestamp = await get_last_timestamp(session, token)
        logger.info("Стартуем с timestamp = %s", last_timestamp)

        await long_poll(session, token, bot, chat_id, last_timestamp)


if __name__ == "__main__":
    asyncio.run(main())
