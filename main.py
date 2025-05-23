import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from steps import steps
from check_subscription import check_user_subscription

load_dotenv()
API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_start_keyboard():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("📋 Шаги", "ℹ️ Инфо")

def get_steps_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [types.KeyboardButton(f"Шаг {step['step']} ({step['duration_min']}м)") for step in steps]
    kb.add(*buttons)
    kb.add("ℹ️ Инфо")
    return kb

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if not await check_user_subscription(bot, message.from_user.id, CHANNEL_USERNAME):
        return await message.answer("Пожалуйста, подпишись на канал @sunxstyle, чтобы продолжить.")
    await message.answer(
        "Привет, солнце! ☀️\nТы в таймере по методу суперкомпенсации.\nКожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n\nНачинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\nКаждый новый день и после перерыва — возвращайся на 2 шага назад.\n\nХочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу.",
        reply_markup=get_start_keyboard()
    )

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer(
        "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
        "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.\n\n"
        "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,\n"
        "и при отсутствии противопоказаний можно загорать без SPF.\n"
        "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.\n\n"
        "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — надевай одежду, головной убор или используй SPF.\n\n"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад."
    )

@dp.message_handler(lambda message: message.text.startswith("Шаг"))
async def handle_step(message: types.Message):
    await message.answer("Скоро будет подробный таймер. Пока только структура готова 🙂")

@dp.message_handler(lambda message: message.text == "📋 Шаги")
async def show_steps(message: types.Message):
    await message.answer("Выбери шаг:", reply_markup=get_steps_keyboard())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)