from aiogram import Bot, Dispatcher
import logging
import asyncio
from app.handler import *

bot = Bot(token='7406747195:AAHApFoswG0YtG-iClZp3OJ8H5ODzo631J0')
dp = Dispatcher()
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
