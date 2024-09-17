import asyncio
import logging
from aiogram import Bot, Dispatcher

from app.handler import router
from aiogram.fsm import FSMContext


bot = Bot(token='7406747195:AAHApFoswG0YtG-iClZp3OJ8H5ODzo631J0')
dp = Dispatcher(bot)

async def main():
    try:
        dp.include_router(router)
        await dp.start_polling()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
