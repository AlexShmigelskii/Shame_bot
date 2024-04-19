from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from funcs.db import check_existing_user, add_new_user

form_router = Router()


@form_router.message(Command("start"),)
async def command_start(message: Message) -> None:

    user_id = message.from_user.id
    start_photo = FSInputFile("start_image.JPG")

    existing_user = check_existing_user(user_id)

    if existing_user:

        await message.bot.send_photo(
            chat_id=user_id,
            photo=start_photo,
            caption="Привет! С возвращением в нашего бота!"
                    "\nСамое время найти новые места для отдыха.",

            reply_markup=ReplyKeyboardRemove()

        )

    else:

        await message.bot.send_photo(
            chat_id=user_id,
            photo=start_photo,
            caption="Привет! Я - бот SHAME. Порекомендую Вам лучшие рестораны, кафе, бары и клубы в центральном "
                    "округе Москвы."
                    
                    "\nПодписывайтесь!",

            reply_markup=ReplyKeyboardRemove()

            )
        # Добавление пользователя в базу данных
        add_new_user(user_id)

