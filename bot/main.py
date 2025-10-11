import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from bot.config import settings
from bot.handlers import start, fallback, cancel

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="cancel", description="Cancel the current action"),
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # подключаем хэндлеры
    dp.include_routers(start.router)
    dp.include_routers(cancel.router)
    dp.include_routers(fallback.router)
    
    await set_commands(bot)
    print("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())