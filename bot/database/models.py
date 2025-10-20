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

    payments = relationship("Payment", back_populates="user")
    summaries = relationship("Summary", back_populates="user")

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
    expires_at = Column(DateTime(timezone=True), nullable=True)  # subscription expiration date

    user = relationship("User", back_populates="payments")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    file_type = Column(String, nullable=False)  # pdf, docx, txt, etc.
    level = Column(String, nullable=False)  # short / medium / detailed
    tokens_used = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # processing time (seconds)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="summaries")