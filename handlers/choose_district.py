from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from funcs.check_subscription import is_subscribed, is_administrator

from keyboards.choose_district_kb import get_district_kb, get_place_kb, get_subscription_kb, get_back_to_district_kb, get_continue_establishments_kb

from funcs.db import check_existing_user, add_new_user, get_establishments, get_photo_paths_for_establishment, \
    log_request

form_router = Router()


@form_router.callback_query(F.data.in_({"choose_district", "check_subscription"}))
async def choose_district(callback_query: CallbackQuery):

    await log_request(callback_query.from_user.id)

    user_id = callback_query.from_user.id
    existing_user = await check_existing_user(user_id)

    if existing_user:
        if await is_subscribed(user_id) or await is_administrator(user_id):
            # Пользователь подписан на канал, позволяем ему выбирать район
            await callback_query.message.edit_text("На связи бот shame. Выбирай район, и я создам подборку лучших "
                                                   "ресторанов, кафе, баров и клубов в этом месте."
                                                   "\nПо вопросам сотрудничества пишите @onesddluv",
                                                   reply_markup=get_district_kb())

        else:
            # Пользователь не подписан на канал, сообщаем ему об этом
            await callback_query.message.edit_text("Для выбора района вы должны подписаться на наш канал!"
                                                   "@shamemedia",
                                                   reply_markup=get_subscription_kb())

    else:
        # Пользователя нет в базе данных и он как-то смог отправить команду
        await add_new_user(user_id)
        await callback_query.message.answer(
            "Привет! Я - бот SHAME. Порекомендую Вам лучшие рестораны, кафе, бары и клубы в "
            "центральном округе Москвы."
            "\nПодписывайтесь!")


@form_router.callback_query(F.data.in_({"Арбат", "Басманный", "Замоскворечье", " Красносельский", "Мещанский",
                                        "Пресненский", "Таганский", "Тверской", "Хамовники", "Якиманка",}))
async def process_chosen_district(callback_query: CallbackQuery, state: FSMContext):

    await log_request(callback_query.from_user.id)

    district = callback_query.data

    await state.update_data(district=district)

    await callback_query.message.edit_text(f'Ты выбрал {district}',
                                           reply_markup=get_place_kb())


@form_router.callback_query(F.data.in_({"Ресторан", "Бар"}))
async def process_chosen_place(callback_query: CallbackQuery, state: FSMContext):

    await log_request(callback_query.from_user.id)

    chat_id = callback_query.from_user.id
    establishment_type = callback_query.data

    data = await state.get_data()
    district = data.get("district")

    # Получаем список заведений из базы данных
    establishments = await get_establishments(district, establishment_type)

    if establishments:
        num_per_message = 3

        remaining_establishments = establishments[num_per_message:] if len(establishments) > num_per_message else []

        for i in range(1):
            start_index = i * num_per_message
            end_index = min((i + 1) * num_per_message, len(establishments))

            for establishment in establishments[start_index:end_index]:
                establishment_id = establishment[0]
                establishment_name = establishment[1]
                establishment_address = establishment[4]
                establishment_metro = establishment[5]
                establishment_description = establishment[6]
                establishment_feature = establishment[7]
                establishment_photo_paths = await get_photo_paths_for_establishment(establishment_id)

                establishment_text = f"{establishment_name}\n\n" \
                                     f"{establishment_feature}\n\n"\
                                     f"📍 {establishment_address}\n" \
                                     f"Ⓜ️ {establishment_metro}\n\n" \
                                     f"{establishment_description}" \

                media_group = MediaGroupBuilder(caption=establishment_text)

                for photo_path in establishment_photo_paths:
                    media_group.add(type="photo", media=FSInputFile(photo_path))

                await callback_query.bot.send_media_group(chat_id=chat_id, media=media_group.build())

        # Сохраняем оставшиеся заведения в состоянии
        await state.update_data(remaining_establishments=remaining_establishments)

        if remaining_establishments:
            await callback_query.bot.send_message(chat_id=chat_id,
                                                  text="Продолжить?",
                                                  reply_markup=get_continue_establishments_kb())
        else:
            await callback_query.bot.send_message(chat_id=chat_id,
                                                  text="Пока что это всё, что я могу тебе предложить по твоему запросу",
                                                  reply_markup=get_back_to_district_kb())

    else:
        await callback_query.message.edit_text(
            f'К сожалению, в районе {district} нет заведений типа {establishment_type}.',
            reply_markup=get_back_to_district_kb())


@form_router.callback_query(F.data.in_({"continue_establishments"}))
async def continue_establishments(callback_query: CallbackQuery, state: FSMContext):

    await log_request(callback_query.from_user.id)

    chat_id = callback_query.from_user.id
    data = await state.get_data()
    remaining_establishments = data.get("remaining_establishments")

    if remaining_establishments:
        num_per_message = 3

        establishments_to_send = remaining_establishments[:num_per_message]
        remaining_establishments = remaining_establishments[num_per_message:]

        for establishment in establishments_to_send:
            establishment_id = establishment[0]
            establishment_name = establishment[1]
            establishment_address = establishment[4]
            establishment_metro = establishment[5]
            establishment_description = establishment[6]
            establishment_feature = establishment[7]
            establishment_photo_paths = await get_photo_paths_for_establishment(establishment_id)

            establishment_text = f"{establishment_name}\n\n" \
                                 f"{establishment_feature}\n\n"\
                                 f"📍 {establishment_address}\n" \
                                 f"Ⓜ️ {establishment_metro}\n\n" \
                                 f"{establishment_description}" \

            media_group = MediaGroupBuilder(caption=establishment_text)

            for photo_path in establishment_photo_paths:
                media_group.add(type="photo", media=FSInputFile(photo_path))

            await callback_query.bot.send_media_group(chat_id=chat_id, media=media_group.build())

        # Сохраняем оставшиеся заведения в состоянии
        await state.update_data(remaining_establishments=remaining_establishments)

        if remaining_establishments:
            await callback_query.bot.send_message(chat_id=chat_id,
                                                  text="Продолжить?",
                                                  reply_markup=get_continue_establishments_kb())
        else:
            await callback_query.bot.send_message(chat_id=chat_id,
                                                  text="Пока что это всё, что я могу тебе предложить по твоему запросу",
                                                  reply_markup=get_back_to_district_kb())

    else:
        await callback_query.answer("Все заведения уже были показаны")
