from aiogram import Router
from .base import router as base_router
from .games import router as games_router

def include_routers(dp):
    """Регистрирует все хендлеры в диспетчере"""
    dp.include_router(games_router)  # Игры первыми
    dp.include_router(base_router)   # Базовые команды вторыми