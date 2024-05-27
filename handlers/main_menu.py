from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, CallbackQuery

from funcs.db import check_existing_user, add_new_user, log_request

from keyboards.main_menu_kb import get_start_kb

form_router = Router()


@form_router.message(Command("start"))
async def command_start(message: Message) -> None:
    log_request(message.from_user.id)

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
        await message.answer("Главное меню:",
                             reply_markup=get_start_kb()
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
        await message.answer("Главное меню:",
                             reply_markup=get_start_kb()
                             )
        # Добавление пользователя в базу данных
        add_new_user(user_id)


@form_router.callback_query(F.data.in_({"back_to_main_menu"}))
async def process_back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(f'Главное меню:',
                                           reply_markup=get_start_kb())
    log_request(callback_query.from_user.id)

