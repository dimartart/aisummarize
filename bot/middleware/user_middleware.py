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
        # Получаем пользователя из события
        tg_user: User = data.get('event_from_user')
        if tg_user:
            # Получаем или создаем пользователя в БД
            db_user = await get_or_create_user(
                telegram_id=tg_user.id,
                username=tg_user.username,
                lang=get_user_language(tg_user.language_code)
            )
            # Добавляем в data для использования в хендлерах
            data['db_user'] = db_user
            data['user_language'] = db_user.language
        
        return await handler(event, data)