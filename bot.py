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
from aiogram.types import InputFile
from database import add_file


# 🔹 Админге арналған файл қосу функциясы
@dp.message_handler(content_types=types.ContentType.DOCUMENT, user_id=123456789)  # <- Өз Telegram ID-ңді жаз
async def handle_file(message: types.Message):
    document = message.document
    await message.reply("📥 Қолданбаның атауын енгізіңіз:")
    
    @dp.message_handler()
    async def get_title(title: types.Message):
        await message.reply("📝 Қысқаша сипаттамасын жазыңыз:")
        
        @dp.message_handler()
        async def get_description(description: types.Message):
            await message.reply("📱 Қолданба қай жүйеге арналған? (Android/Windows)")

            @dp.message_handler()
            async def get_os(os: types.Message):
                await message.reply("🔓 Взлом түрін таңдаңыз: (Взлом, Премиум, Ақылы)")
                
                @dp.message_handler()
                async def get_feature(feature: types.Message):
                    # Файлды базаға қосу
                    add_file(document.file_id, title.text, description.text, os.text, feature.text)
                    
                    # Түйме жасау
                    btn_download = InlineKeyboardMarkup().add(
                        InlineKeyboardButton("📥 Жүктеп алу", callback_data=f"download_{document.file_id}")
                    )
                    
                    # Арнаға пост жіберу
                    post_text = f"""
<b>{title.text}</b>

📌 {description.text}
🖥 Жүйе: {os.text}
🔓 Мүмкіндік: {feature.text}

⬇ Төмендегі түйме арқылы жүктеп алыңыз:
                    """
                    await bot.send_document(config.CHANNEL_USERNAME, document.file_id, caption=post_text, reply_markup=btn_download)
                    await message.reply("✅ Қолданба сәтті жарияланды!")

from aiogram.types import ChatMemberStatus
import config  # <- Тіркеу керек арна ID-сы config файлына жазылуы керек

# 🔹 Қолданушы арнаға тіркелген бе, тексереміз
async def is_subscribed(user_id):
    member = await bot.get_chat_member(config.CHANNEL_USERNAME, user_id)
    return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
from aiogram.types import InputFile
from aiogram.utils.exceptions import ChatNotFound
from database import conn, cursor

# 🔹 Қолданушы "Жүктеп алу" түймесін басқанда
@dp.callback_query_handler(lambda c: c.data.startswith("download_"))
async def send_file(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    file_id = callback_query.data.split("_")[1]

    # 🔹 Арнаға тіркелгенін тексеру
    if not await is_subscribed(user_id):
        btn_subscribe = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Арнаға жазылу", url=f"https://t.me/{config.CHANNEL_USERNAME[1:]}")
        )
        await bot.send_message(user_id, "⚠ Жүктеп алу үшін алдымен арнаға жазылыңыз!", reply_markup=btn_subscribe)
        return

    # 🔹 Дерекқордан файлды алу
    cursor.execute("SELECT file_id, title FROM files WHERE file_id = ?", (file_id,))
    file_data = cursor.fetchone()

    if file_data:
        await bot.send_document(user_id, file_data[0], caption=f"📂 {file_data[1]}")
        await callback_query.answer("📥 Файл жіберілді!", show_alert=True)
    else:
        await callback_query.answer("⚠ Файл табылмады!", show_alert=True)

# 🔹 Ботты іске қосу
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
