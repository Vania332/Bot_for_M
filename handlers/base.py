from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import AsyncSessionLocal
from repository import UserRepository

router = Router()
user_repo = UserRepository()

@router.message(Command("start"))
async def start(msg: Message):
    if msg.chat.type != "private":
        await msg.reply(f"👋 Напиши мне в личку /start для регистрации \
                        \n   - /coin <<сумма>> \
                        \n   - /balance ")
        return
    
    async with AsyncSessionLocal() as session:
        user = await user_repo.get_or_create(session, msg.from_user.id, msg.from_user.username)
        await session.commit()
    
    await msg.answer(
        f"🎰 Добро пожаловать, {msg.from_user.first_name}!\n"
        f"💰 Баланс: {user.balance} 🪙\n\n"
        f"🎯 Игры:\n"
        f"/coin <ставка> — орёл или решка ×2"
    )

@router.message(Command("balance"))
async def balance(msg: Message):
    async with AsyncSessionLocal() as session:
        user = await user_repo.get_or_create(session, msg.from_user.id, msg.from_user.username)
        balance = user.balance
    
    name = msg.from_user.first_name or "Игрок"
    await msg.reply(f"💰 {name}, твой баланс: {balance} 🪙")    