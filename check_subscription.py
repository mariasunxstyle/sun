from aiogram import Bot
from aiogram.utils.exceptions import ChatNotFound

async def check_user_subscription(bot: Bot, user_id: int, channel_username: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except ChatNotFound:
        return False