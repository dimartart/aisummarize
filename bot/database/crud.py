from sqlalchemy import select, update
from bot.database.models import User
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

async def update_language(telegram_id: int, lang: str):
    async with async_session() as session:
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(language=lang)
        )
        await session.commit()

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