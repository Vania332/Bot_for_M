import os 
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base

load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не найден в .env")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"server_settings": {"timezone": "Europe/Moscow"}}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  
)


async def init_db():
    """Создаёт таблицы при первом запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)