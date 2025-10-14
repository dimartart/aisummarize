from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from bot.database.crud import get_or_create_user
from bot.services.i18n import get_user_language

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        tg_user: User = data.get('event_from_user')
        if tg_user:
            # Get or create user in DB
            db_user = await get_or_create_user(
                telegram_id=tg_user.id,
                username=tg_user.username,
                lang=get_user_language(tg_user.language_code)
            )
            # Add user info to data for handlers
            data['db_user'] = db_user
            data['user_language'] = db_user.language
        
        return await handler(event, data)