import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from steps import steps
from check_subscription import check_user_subscription
import asyncio

load_dotenv()
API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_states = {}

def get_steps_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for step in steps:
        kb.insert(types.KeyboardButton(f"Шаг {step['step']} ({step['duration_min']}м)"))
    kb.add("ℹ️ Инфо")
    return kb

def get_subscribe_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔗 Перейти к каналу", url="https://t.me/sunxstyle"))
    kb.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_sub"))
    return kb

def get_control_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("⏭️ Пропустить", callback_data="skip"),
        InlineKeyboardButton("⛔ Завершить", callback_data="end"),
        InlineKeyboardButton("↩️ Назад на 2 шага", callback_data="back"),
        InlineKeyboardButton("📋 Вернуться к шагам", callback_data="menu")
    )
    return kb

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if not await check_user_subscription(bot, message.from_user.id, CHANNEL_USERNAME):
        return await message.answer("Пожалуйста, подпишись на канал @sunxstyle, чтобы продолжить.", reply_markup=get_subscribe_keyboard())

    await message.answer(
        "Привет, солнце! ☀️\nТы в таймере по методу суперкомпенсации.\nКожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n\nНачинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\nКаждый новый день и после перерыва — возвращайся на 2 шага назад."
    )
    await message.answer("Выбери шаг:", reply_markup=get_steps_keyboard())

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def recheck_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_user_subscription(bot, user_id, CHANNEL_USERNAME):
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, "Спасибо за подписку!")
        await bot.send_message(user_id, "Выбери шаг:", reply_markup=get_steps_keyboard())
    else:
        await bot.answer_callback_query(callback_query.id, text="Ты всё ещё не подписан!", show_alert=True)

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
    try:
        step_num = int(message.text.split()[1])
        step_data = next(s for s in steps if s["step"] == step_num)
    except Exception:
        return await message.answer("Не удалось определить шаг.")

    user_id = message.from_user.id
    user_states[user_id] = {"step": step_num, "pos": 0, "cancel": False}
    await message.answer(f"⚡️ Шаг {step_num} ({step_data['duration_min']} мин)", reply_markup=get_control_keyboard()  # standard controls with Пропустить)

    for idx, position in enumerate(step_data["positions"]):
        if user_states[user_id]["cancel"]:
            return
        user_states[user_id]["pos"] = idx
        await message.answer(f"{position} — {step_data['duration_min']} мин", reply_markup=get_control_keyboard()  # standard controls with Пропустить)
        await asyncio.sleep(1)

    await message.answer("✅ Шаг завершён!")\nawait message.answer("Продолжить или выбрать другой шаг:", reply_markup=get_control_keyboard()  # standard controls with Пропустить)
    user_states.pop(user_id, None)

@dp.callback_query_handler(lambda c: c.data in ["skip", "end", "menu", "back"])
async def handle_controls(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "skip":
        await bot.answer_callback_query(callback_query.id, text="Пропускаем позицию")
        if user_id in user_states:
            user_states[user_id]["pos"] += 1
    elif data == "end":
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, "Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=get_steps_keyboard())
        user_states[user_id]["cancel"] = True
    elif data == "menu":
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, "Выбери шаг:", reply_markup=get_steps_keyboard())
        user_states[user_id]["cancel"] = True
    elif data == "continue":
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(user_id, "Выбери шаг:", reply_markup=get_steps_keyboard())
        user_states.pop(user_id, None)
    elif data == "back":
        await bot.answer_callback_query(callback_query.id)
        step = max(user_states.get(user_id, {}).get("step", 3) - 2, 1)
        await bot.send_message(user_id, f"Возвращаемся на шаг {step}", reply_markup=get_steps_keyboard())
        user_states[user_id]["cancel"] = True

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

def get_post_step_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("▶️ Продолжить", callback_data="continue"),
        InlineKeyboardButton("⛔ Завершить", callback_data="end"),
        InlineKeyboardButton("↩️ Назад на 2 шага", callback_data="back"),
        InlineKeyboardButton("📋 Вернуться к шагам", callback_data="menu")
    )
    return kb