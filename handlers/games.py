import random
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import AsyncSessionLocal
from repository import UserRepository
from game_logic.coin import play_coin  

router = Router()
user_repo = UserRepository()

@router.message(Command("coin"))
async def coin(msg: Message):
    # Валидация
    if msg.chat.type == "private":
        await msg.reply("🎲 Играй в группе!")
        return
    
    try:
        bet = int(msg.text.split()[1])
    except (IndexError, ValueError):
        await msg.reply("❓ Используй: /coin 50")
        return
    
    if bet < 10:
        await msg.reply("⚠️ Минимум 10 монет")
        return

    # Логика
    async with AsyncSessionLocal() as session:
        # Получаем пользователя
        user = await user_repo.get_or_create(session, msg.from_user.id, msg.from_user.username)
        
        # Проверяем баланс (атомарно)
        success = await user_repo.try_bet(session, msg.from_user.id, bet)
        if not success:
            await msg.reply("❌ Недостаточно монет")
            return
        
        win, payout = play_coin(bet)  
        
        # Если выигрыш — добавляем монеты
        if win:
            await user_repo.add_balance(session, msg.from_user.id, payout)
        
        # Получаем новый баланс
        new_balance = await user_repo.get_balance(session, msg.from_user.id)
        await session.commit()
    
    # Ответ в чат
    name = msg.from_user.first_name or "Игрок"
    result_text = f"✅ ОРЁЛ — ВЫИГРЫШ +{payout}!" if win else "❌ РЕШКА — ПРОИГРЫШ"
    await msg.reply(
        f"🪙 {name} поставил {bet} монет\n"
        f"{result_text}\n"
        f"💰 Баланс: {new_balance} 🪙"
    )