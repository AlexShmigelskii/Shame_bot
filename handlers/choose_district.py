from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from funcs.check_subscription import is_subscribed


from funcs.db import check_existing_user, add_new_user

form_router = Router()


@form_router.message(Command("choose_district"))
async def choose_district(message: Message):
    user_id = message.from_user.id
    existing_user = check_existing_user(user_id)

    if existing_user:
        if await is_subscribed(user_id):
            # Пользователь подписан на канал, позволяйте ему выбирать район
            await message.answer("Выберите район:")

            # Добавьте здесь дополнительные действия для выбора района
        else:
            # Пользователь не подписан на канал, сообщите ему об этом
            await message.answer("Для выбора района вы должны подписаться на наш канал!")

    else:
        add_new_user(user_id)
        await message.answer("Привет! Я - бот SHAME. Порекомендую Вам лучшие рестораны, кафе, бары и клубы в "
                             "центральном округе Москвы."
                             "\nПодписывайтесь!")
