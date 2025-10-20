from sqlalchemy import select, update
from bot.database.models import User, Summary
from bot.database.session import async_session

async def get_or_create_user(telegram_id: int, username: str = None, lang: str = "en"):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username, language=lang)
            session.add(user)
            await session.commit()
        return user

async def decrement_summary(telegram_id: int):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id, User.summaries_left > 0)
            .values(summaries_left=User.summaries_left - 1)
        )
        await session.commit()

async def set_premium(telegram_id: int, status: bool):
    async with async_session() as session:
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_premium=status)
        )
        await session.commit()

async def update_user_language(user_id: int, lang: str):
    async with async_session() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(language=lang)
        )
        await session.commit()

async def create_summary_record(
    user_id: int,
    file_type: str = None,
    level: str = None,
    tokens_used: int = None,
    duration: float = None,
    success: bool = True
) -> Summary:
    """Create a new summary record in the database"""
    async with async_session() as session:
        summary = Summary(
            user_id=user_id,
            file_type=file_type,
            level=level,
            tokens_used=tokens_used,
            duration=duration,
            success=success
        )
        session.add(summary)
        await session.commit()
        await session.refresh(summary)
        return summary