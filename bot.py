import asyncio
import random
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from database import init_db, AsyncSessionLocal
from repository import UserRepository

# Загрузка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
user_repo = UserRepository()  # Один экземпляр на всё приложение

# ==================== ХЕНДЛЕРЫ ====================

@router.message(Command("start"))
async def start(msg: Message):
    """Регистрация пользователя (только в личке)"""
    if msg.chat.type != "private":
        await msg.reply(
            "👋 Привет! Я казино-бот с виртуальной валютой.\n"
            "Для регистрации напиши мне в личку: /start"
        )
        return
    
    async with AsyncSessionLocal() as session:
        user = await user_repo.get_or_create(
            session,
            user_id=msg.from_user.id,
            username=msg.from_user.username
        )
        await session.commit()
    
    await msg.answer(
        f"🎰 Добро пожаловать, {msg.from_user.first_name}!\n\n"
        f"💰 Твой баланс: {user.balance} 🪙\n\n"
        f"🎯 Доступные команды:\n"
        f"• /coin <ставка> — орёл или решка (×2)\n"
        f"• /balance — проверить баланс\n"
        f"• /daily — ежедневный бонус +200 🪙\n\n"
        f"⚠️ Это развлекательный бот с ВИРТУАЛЬНОЙ валютой. "
        f"Никаких реальных денег и выплат!"
    )

@router.message(Command("balance"))
async def balance(msg: Message):
    """Показать баланс"""
    async with AsyncSessionLocal() as session:
        user = await user_repo.get_or_create(
            session,
            user_id=msg.from_user.id,
            username=msg.from_user.username
        )
        balance = user.balance
    
    name = msg.from_user.first_name or "Игрок"
    await msg.reply(f"💰 {name}, твой баланс: {balance} 🪙")

@router.message(Command("daily"))
async def daily(msg: Message):
    """Ежедневный бонус +200 монет"""
    async with AsyncSessionLocal() as session:
        if not await user_repo.can_claim_bonus(session, msg.from_user.id):
            await msg.reply("🎁 Бонус можно забрать раз в 24 часа. Приходи завтра! ⏰")
            return
        
        await user_repo.add_balance(session, msg.from_user.id, 200)
        await user_repo.set_bonus_time(session, msg.from_user.id)
        await session.commit()
    
    await msg.reply("🎁 +200 монет! Удачи в игре 🎊")

@router.message(Command("coin"))
async def coin(msg: Message):
    """Орёл/решка — только в группах"""
    # Работаем только в группах
    if msg.chat.type == "private":
        await msg.reply("🎲 Эту команду нужно использовать в группе! Добавь меня в чат.")
        return
    
    # Игнорируем других ботов
    if msg.from_user.is_bot:
        return
    
    # Парсинг ставки
    args = msg.text.split()
    if len(args) < 2:
        await msg.reply("❓ Использование: `/coin 50`", parse_mode="Markdown")
        return
    
    try:
        bet = int(args[1])
    except ValueError:
        await msg.reply("❌ Ставка должна быть целым числом")
        return

    if bet < 10:
        await msg.reply("⚠️ Минимальная ставка: 10 монет")
        return
    
    # Атомарная ставка в одной транзакции
    async with AsyncSessionLocal() as session:
        # Получаем/создаём пользователя
        user = await user_repo.get_or_create(
            session,
            user_id=msg.from_user.id,
            username=msg.from_user.username
        )
        
        # Пытаемся списать ставку (атомарно!)
        success = await user_repo.try_bet(session, msg.from_user.id, bet)
        if not success:
            await msg.reply("❌ Недостаточно монет для ставки")
            return
        
        # 49% шанс выигрыша (казино в плюсе 😈)
        win = random.random() > 0.51
        if win:
            await user_repo.add_balance(session, msg.from_user.id, bet * 2)
        
        # Получаем актуальный баланс
        balance = await user_repo.get_balance(session, msg.from_user.id)
        await session.commit()
    
    # Формируем ответ
    name = msg.from_user.first_name or "Игрок"
    result_emoji = "✅ ОРЁЛ" if win else "❌ РЕШКА"
    result_text = "ВЫИГРЫШ!" if win else "ПРОИГРЫШ"
    
    await msg.reply(
        f"🪙 {name} поставил {bet} монет!\n"
        f"{result_emoji} — {result_text}\n"
        f"💰 Баланс: {balance} 🪙"
    )

# ==================== ЗАПУСК ====================

async def main():
    # Инициализация БД
    await init_db()
    
    # Регистрация роутера
    dp.include_router(router)
    
    # Информация о боте
    bot_info = await bot.get_me()
    print(f"\n✅ Бот @{bot_info.username} успешно запущен")
    print(f"🔧 Настройка для групп:")
    print(f"   1. Добавь бота в группу")
    print(f"   2. Дай права администратора → включи 'Читать сообщения'")
    print(f"   3. Каждый игрок пишет боту в личку /start для регистрации")
    print(f"   4. В группе используй: /coin 50\n")
    
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())