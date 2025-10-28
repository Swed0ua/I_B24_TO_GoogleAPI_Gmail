import asyncio
from enum import Enum
import sys
import traceback
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from types_file import BANK_NAMES

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_BOT2_TOKEN = os.getenv("TG_BOT2_TOKEN")

GROUP_ID = int(os.getenv("GROUP_ID"))
GROUP2_ID = int(os.getenv("GROUP2_ID"))
GROUP2_THREAD_ID = int(os.getenv("GROUP2_THREAD_ID"))

GROUP_СASH_REGISTER = int(os.getenv("GROUP_CASH_REGISTER_ID"))

GROUP_THAYAVKA_ID = int(os.getenv("GROUP_THAYAVKA_ID"))


GROUP_BANKS_ID = {
    BANK_NAMES.PUMB: int(os.getenv("GROUP_PUMB_ID")),
    BANK_NAMES.RAIFF: int(os.getenv("GROUP_RAIFF_ID")),
    BANK_NAMES.OKSI: int(os.getenv("GROUP_OKSI_ID")),
    BANK_NAMES.PIVDENNUY: int(os.getenv("GROUP_PIVDENNUY_ID")),
    BANK_NAMES.OSCHAD: int(os.getenv("GROUP_OSCHAD_ID")),
    BANK_NAMES.ABANK: int(os.getenv("GROUP_ABANK_ID")),
    BANK_NAMES.VOSTOK: int(os.getenv("GROUP_VOSTOK_ID"))
}

# Ініціалізація бота та диспетчера
dp = Dispatcher()

bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot2 = Bot(token=TG_BOT2_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def send_message_to_group(text: str, group_id=GROUP_ID):
    """
    Асинхронна функція для відправлення повідомлення в групу.

    :param text: Текст повідомлення
    """
    try:
        print("send_message_to_group", text)
        await bot.send_message(chat_id=group_id, text=text)
    except Exception as e:
        print(f"Помилка при відправленні повідомлення: {e}")

async def send_message_to_group_bot2(text: str, group_id=GROUP_СASH_REGISTER):
    """
    Асинхронна функція для відправлення повідомлення в групу.

    :param text: Текст повідомлення
    """
    try:
        print("send_message_to_group_bot2", text)
        await bot2.send_message(text=text, chat_id=group_id)
    except Exception as e:
        print(f"Помилка при відправленні повідомлення: {e}")

async def send_message_to_group_service_support(text: str):
    """
    Асинхронна функція для відправлення повідомлення в групу.

    :param text: Текст повідомлення
    """
    try:
        print("send_message_to_group_service_support", text)
        # await bot2.send_message(chat_id=GROUP2_ID, text=text, message_thread_id=GROUP2_THREAD_ID)
        await bot2.send_message(chat_id=GROUP_THAYAVKA_ID, text=text)
    except Exception as e:
        print(f"Помилка при відправленні повідомлення: {e}")

async def send_message_to_group_bank_supports(text: str, bank_tp:BANK_NAMES):
    """
    Асинхронна функція для відправлення повідомлення в групу.

    :param text: Текст повідомлення
    :param text: Bank type for send in thier group
    """
    try:
        print("send_message_to_group_bank_supports", text, bank_tp)
        if bank_tp in GROUP_BANKS_ID:
            lines = text.replace("span", "b").split("\n")
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            new_text = "\n".join(cleaned_lines)

            await bot2.send_message(chat_id=GROUP_BANKS_ID[bank_tp], text=new_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Помилка при відправленні повідомлення: {e}")

async def get_group_id(message: Message):
    """
    Обробник команди /id, який виводить ID групи в консоль.

    :param message: Об'єкт повідомлення
    """
    chat_id = message.chat.id
    # message_thread_id = message.message_thread_id
    print(f"ID групи: {chat_id}")
    await message.reply(f"ID цієї групи: {chat_id}")

# Реєстрація обробника
dp.message.register(get_group_id, Command(commands=["id"]))

async def start_telegram_bot():
    """
    Функція для запуску Telegram-бота.
    """
    await dp.start_polling(bot2)

async def main():
    """
    Головна функція для запуску бота та збереження доступу до інших функцій.
    """
    bot_task = asyncio.create_task(start_telegram_bot())
    print("Бот запущений. Ви можете використовувати send_message_to_group().")
    await bot_task

if __name__ == "__main__":
    asyncio.run(main()) 