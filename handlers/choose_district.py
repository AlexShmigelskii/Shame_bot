from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from Forms.choose_district_form import Form
from funcs.check_subscription import is_subscribed

from keyboards.choose_district_kb import get_district_kb, get_place_kb, get_subscription_kb

from funcs.db import check_existing_user, add_new_user

form_router = Router()


@form_router.callback_query(F.data.in_({"choose_district", "check_subscription"}))
async def choose_district(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    existing_user = check_existing_user(user_id)

    if existing_user:
        if await is_subscribed(user_id):
            # Пользователь подписан на канал, позволяем ему выбирать район
            await callback_query.message.edit_text("Выберите район:",
                                                   reply_markup=get_district_kb())

        else:
            # Пользователь не подписан на канал, сообщаем ему об этом
            await callback_query.message.edit_text("Для выбора района вы должны подписаться на наш канал!",
                                                   reply_markup=get_subscription_kb())

    else:
        # Пользователя нет в базе данных и он как-то смог отправить команду
        add_new_user(user_id)
        await callback_query.message.answer(
            "Привет! Я - бот SHAME. Порекомендую Вам лучшие рестораны, кафе, бары и клубы в "
            "центральном округе Москвы."
            "\nПодписывайтесь!")


@form_router.callback_query(F.data.in_({"Арбат", "Басманный", "Замоскворечье", " Красносельский", "Мещанский",
                                        "Пресненский", "Таганский", "Тверской", "Хамовники", "Якиманка",
                                        }))
async def process_chosen_district(callback_query: CallbackQuery, state: FSMContext):
    district = callback_query.data

    await state.update_data(district=district)

    await callback_query.message.edit_text(f'Ты выбрал {district}',
                                           reply_markup=get_place_kb())


@form_router.callback_query(F.data.in_({"Ресторан", "Бар"}))
async def process_chosen_place(callback_query: CallbackQuery, state: FSMContext):
    place = callback_query.data

    await state.update_data(place=place)

    data = await state.get_data()  # Здесь хранятся район и место!

    district = data.get("district")
    place_1 = data.get("place")

    await callback_query.message.edit_text(f'Ты выбрал {place_1} в районе {district}')
