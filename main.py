import asyncio

import logging
import sys

import secret
from essentials import dp, bot
from funcs.db import create_database
from handlers import main_menu, choose_district


# Запуск бота
async def main():
    dp.include_routers(
        main_menu.form_router,
        choose_district.form_router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Создаем цикл событий asyncio
async def run():
    await asyncio.gather(main())  # Запускаем бота и планировщик задач

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    create_database()
    asyncio.run(run())
