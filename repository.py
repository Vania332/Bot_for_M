from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from database import AsyncSessionLocal

class UserRepository:
    
    """Репозиторий для работы с пользователями (сессия передаётся в каждый метод)"""
    
    
    async def get_or_create(self, session: AsyncSession, user_id: int, username: str | None = None) -> User:
        
        """Получить или создать(если нет) пользователя"""
        
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none() 
        
        if not user:
            user = User(user_id=user_id, username=username)
            session.add(user)
            
        if username and user.username != username:
            user.username = username
            
        return user
    
    async def try_bet(self, session: AsyncSession, user_id: int, bet: int) -> bool:
        """
        Атомарно списывает ставку с баланса.
        Возвращает: True если ставка прошла, False если недостаточно средств.
        """
        result = await session.execute(update(User).where(User.user_id == user_id, User.balance >= bet).values(balance=User.balance - bet))
        return result.rowcount > 0 
    
    
    async def add_balance(self, session: AsyncSession, user_id: int, amount: int):
        
        """Добавить монеты к балансу"""

        await session.execute(update(User).where(User.user_id == user_id).values(balance=User.balance + amount))
    
    
    async def can_claim_bonus(self, session: AsyncSession, user_id: int) -> bool:
        
        """Проверить, можно ли забрать ежедневный бонус (прошло 24ч)"""
        
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.last_bonus:
            return True
        
        time_since_bonus = datetime.now(user.last_bonus.tzinfo) - user.last_bonus # @
        return time_since_bonus >= timedelta(hours=24)
    
    
    async def set_bonus_time(self, session: AsyncSession, user_id: int):
        """Обновить время последнего бонуса"""
        await session.execute(update(User).where(User.user_id == user_id).values(last_bonus=datetime.now()))
        
    
    async def get_balance(self, session: AsyncSession, user_id: int) -> int:
        """Получить текущий баланс"""
        result = await session.execute(select(User.balance).where(User.user_id == user_id))
        balance = result.scalar_one_or_none()
        return balance if balance is not None else 1000