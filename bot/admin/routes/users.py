from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select, func
from bot.database.session import async_session
from bot.database.models import User, Summary
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

@router.get("/api/statistics")
async def get_statistics(year: int = None, month: int = None):
    """API endpoint для получения статистики по суммаризациям"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    if year is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    async with async_session() as session:
        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query summaries for the specified month
        result = await session.execute(
            select(Summary)
            .where(
                Summary.created_at >= start_date,
                Summary.created_at < end_date
            )
            .order_by(Summary.created_at)
        )
        summaries = result.scalars().all()
        
        # Count summaries per day
        daily_counts = defaultdict(int)
        for summary in summaries:
            day = summary.created_at.day
            daily_counts[day] += 1
        
        # Create array with counts for each day (1-31)
        days_in_month = (end_date - timedelta(days=1)).day
        data = [daily_counts.get(day, 0) for day in range(1, days_in_month + 1)]
        
        return {
            "year": year,
            "month": month,
            "days_in_month": days_in_month,
            "data": data,
            "total": sum(data)
        }

@router.get("/api/metrics")
async def get_metrics():
    """API endpoint для получения метрик активности пользователей"""
    from datetime import datetime, timedelta, timezone
    
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)
    last_30d = now - timedelta(days=30)
    
    async with async_session() as session:
        # Get users who made summaries in last 24 hours (DAU)
        result_dau = await session.execute(
            select(func.count(func.distinct(Summary.user_id)))
            .where(Summary.created_at >= last_24h)
        )
        dau = result_dau.scalar() or 0
        
        # Get users who made summaries in last 30 days (MAU)
        result_mau = await session.execute(
            select(func.count(func.distinct(Summary.user_id)))
            .where(Summary.created_at >= last_30d)
        )
        mau = result_mau.scalar() or 0
        
        # Calculate DAU/MAU ratio
        dau_mau_ratio = round((dau / mau * 100), 2) if mau > 0 else 0
        
        return {
            "dau": int(dau),
            "mau": int(mau),
            "dau_mau_ratio": float(dau_mau_ratio)
        }


@router.get("/api/summary-stats")
async def get_summary_stats():
    """API endpoint для получения общей статистики по суммаризациям"""
    async with async_session() as session:

        # Get total count of summaries
        result = await session.execute(select(func.count(Summary.id)))
        total_summaries = result.scalar() or 0

        return {
            "total_summaries": int(total_summaries)
        }