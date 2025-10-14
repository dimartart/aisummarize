from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.types import JSON, Float
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String, nullable=True)
    language = Column(String, default="en")
    summaries_left = Column(Integer, default=20)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Добавить эти связи
    payments = relationship("Payment", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount_usd = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_type = Column(String, nullable=False)  # one_time / subscription
    provider = Column(String, nullable=False)  # stripe / telegram / ton / manual
    provider_payment_id = Column(String, nullable=True, unique=True)
    status = Column(String, default="pending")  # pending / success / failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # для подписки

    # связь
    user = relationship("User", back_populates="payments")


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    event = Column(String, nullable=False)  # summary_created, language_changed, payment_success
    analytics_metadata = Column(JSON, nullable=True)  # дополнительные данные
    duration = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # связь
    user = relationship("User", back_populates="analytics")