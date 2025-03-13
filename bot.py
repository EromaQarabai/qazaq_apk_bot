import logging
import config
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Логтарды қосу
logging.basicConfig(level=logging.INFO)

# Ботты бастау
bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# 🔹 Арнаға жазылғанын тексеретін функция
async def check_subscription(user_id):
    chat_member = await bot.get_chat_member(config.CHANNEL_USERNAME, user_id)
    return chat_member.is_chat_member()

# 🔹 "Жүктеп алу" батырмасын басқанда тексеру
@dp.callback_query_handler(lambda c: c.data.startswith("download_"))
async def process_download(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    file_id = callback_query.data.split("_")[1]  # Файл ID (кейін базадан аламыз)

    # Қолданушы тіркелген бе?
    if await check_subscription(user_id):
        await bot.send_message(user_id, f"✅ Қолданба жүктеуге дайын!")
        await bot.send_document(user_id, file_id)
    else:
        btn_subscribe = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Арнаға жазылу", url=f"https://t.me/{config.CHANNEL_USERNAME[1:]}")
        )
        await bot.send_message(user_id, "❌ Алдымен арнаға тіркеліңіз!", reply_markup=btn_subscribe)

# 🔹 Ботты іске қосу
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
