import asyncio
import logging

from aiogram import Bot, Dispatcher

from init_bot import bot

from src.sql.connect import init_db_models
from routers import router

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s [%(asctime)s]: %(message)s (Line: %(lineno)d) [%(filename)s]',
                    datefmt='%d/%m/%Y %I:%M:%S',
                    encoding='utf-8')

dp = Dispatcher()




async def main() -> None:
    dp.startup.register(init_db_models)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
