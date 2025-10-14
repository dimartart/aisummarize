import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from bot.admin.routes import users

app = FastAPI(title="AI Summarize Admin", version="1.0.0")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="bot/admin/static"), name="static")

# Подключение роутов
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)