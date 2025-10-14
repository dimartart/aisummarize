from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from bot.database.session import async_session
from bot.database.models import User
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="bot/admin/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Главная страница админки co списком пользователей"""
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        
        # Конвертируем пользователей в словари для шаблона
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username or "N/A",
                "language": user.language,
                "summaries_left": user.summaries_left,
                "is_premium": user.is_premium,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "N/A",
                "updated_at": user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else "N/A"
            })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "users": users_data,
        "total_users": len(users_data)
    })

@router.get("/api/users")
async def get_users():
    """API endpoint для получения списка пользователей"""
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "language": user.language,
                "summaries_left": user.summaries_left,
                "is_premium": user.is_premium,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            })
    
    return {"users": users_data, "total": len(users_data)}
