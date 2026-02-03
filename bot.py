import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
from handlers.__init__ import include_routers  # Регистрация хендлеров

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    await init_db()
    include_routers(dp)  # ← Подключаем все хендлеры
    bot_info = await bot.get_me()
    print(f"\n✅ Бот @{bot_info.username} запущен")
    print("🔧 Добавь бота в группу и дай права 'Читать сообщения'\n")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())