import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from middleware import LoggingMiddleware
from handlers.profile_handlers import router as profile_router
from handlers.log_handlers import router as log_router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(profile_router, log_router)
dp.message.middleware(LoggingMiddleware())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
