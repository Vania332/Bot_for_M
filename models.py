from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from typing import Optional


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="users"
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=1000) # валюта
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_bonus: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) 
    