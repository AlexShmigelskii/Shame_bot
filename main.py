import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from secret import BOT_TOKEN
from handlers import main_menu, admin, choose_district
from funcs.openai_helper import init_context_db
from funcs.db import create_database

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
async def main():
    await create_database()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(main_menu.form_router)
    dp.include_router(admin.form_router)
    dp.include_router(choose_district.form_router)

    # Инициализируем базу данных для контекста
    init_context_db()
    
    # Запускаем бота
    await dp.start_polling(bot)


# Создаем цикл событий asyncio
async def run():
    await asyncio.gather(main())  # Запускаем бота
    # await populate_db()


if __name__ == "__main__":
    asyncio.run(run())
