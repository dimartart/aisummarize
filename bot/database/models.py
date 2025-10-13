from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)           # внутренний ID
    telegram_id = Column(Integer, unique=True)       # Telegram user_id
    username = Column(String, nullable=True)
    language = Column(String, default="en")          # язык интерфейса
    summaries_left = Column(Integer, default=20)     # оставшиеся попытки
    is_premium = Column(Boolean, default=False)      # подписка активна?
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
