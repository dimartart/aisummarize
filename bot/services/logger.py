import json
from datetime import datetime
from bot.database.session import async_session
from bot.database.models import Analytics

async def log_event(user_id: int, event: str, metadata: dict | None = None, success: bool = True, duration: float | None = None):
    """Записывает событие пользователя в таблицу analytics."""
    async with async_session() as session:
        analytics = Analytics(
            user_id=user_id,
            event=event,
            analytics_metadata=json.dumps(metadata or {}),
            success=success,
            duration=duration,
            created_at=datetime.utcnow()
        )
        session.add(analytics)
        await session.commit()
