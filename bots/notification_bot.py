import asyncio
import logging
import os
import pandas as pd
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiofiles

# Настройки
MAIN_TOKEN = os.environ['BOT_TOKEN']
TEMPLATE_CSV_URL = os.environ['MESSAGES_TABLE_URL']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=MAIN_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class CreateBotStates(StatesGroup):
    waiting_name = State()
    waiting_username = State()
    waiting_token = State()


# Глобальный словарь для хранения задач ботов (в проде — БД)
running_bots = {}


@dp.message(Command('start'))
async def start_handler(message: types.Message):
    await message.reply(
        "🤖 *Основной бот для создания постеров*\n\n"
        "/createbot — создать нового постера\n"
        "/listbots — список активных ботов",
        parse_mode='Markdown'
    )


@dp.message(Command('createbot'))
async def create_bot_start(message: types.Message, state: FSMContext):
    await message.reply("Введите *имя* нового бота:")
    await state.set_state(CreateBotStates.waiting_name)


@dp.message(CreateBotStates.waiting_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.reply("👤 Введите *username* бота (без _bot):")
    await state.set_state(CreateBotStates.waiting_username)


@dp.message(CreateBotStates.waiting_username)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.reply(
        "🔑 *Создайте бота в @BotFather:*\n"
        "1. /newbot\n"
        "2. Имя: [ваше имя]\n"
        "3. Username: @[ваше_username]bot\n"
        "4. *Отправьте сюда полученный токен*",
        parse_mode='Markdown'
    )
    await state.set_state(CreateBotStates.waiting_token)


@dp.message(CreateBotStates.waiting_token)
async def get_token(message: types.Message, state: FSMContext):
    token = message.text.strip()

    data = await state.get_data()
    name, username = data['name'], data['username']

    await message.reply(f"✅ Создаём постера для {name} (@{username}_bot)...")

    # Создаём уникальную CSV ссылку (в проде — копировать шаблон через API)
    bot_csv_url = TEMPLATE_CSV_URL  # Пока используем общий шаблон

    # Сохраняем токен
    token_file = f"{username}.token"
    async with aiofiles.open(token_file, 'w') as f:
        await f.write(token)

    # Запускаем дочернего бота
    task = asyncio.create_task(run_child_bot(token, bot_csv_url, username))
    running_bots[username] = {'task': task, 'csv_url': bot_csv_url}

    await message.reply(
        f"🚀 *Постер @{username}bot запущен!*\n\n"
        f"📊 Таблица: {bot_csv_url}\n"
        f"📝 Заполните посты и сохраните публичный доступ",
        parse_mode='Markdown'
    )
    await state.clear()


@dp.message(Command('listbots'))
async def list_bots(message: types.Message):
    if not running_bots:
        await message.reply("Нет активных ботов")
        return

    text = "*Активные постеры:*\n\n"
    for username, data in running_bots.items():
        status = "🟢 онлайн" if data['task'].done() is False else "🔴 остановлен"
        text += f"• @{username} {status}\n"
    await message.reply(text, parse_mode='Markdown')


async def run_child_bot(token: str, csv_url: str, username: str):
    """Дочерний бот для постинга"""
    child_bot = Bot(token=token)
    scheduler = AsyncIOScheduler()

    async def load_and_schedule_posts():
        try:
            df = pd.read_csv(csv_url)
            logging.info(f"Загружено {len(df)} постов из {csv_url}")