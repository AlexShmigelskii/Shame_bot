from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import random
from secret import ADMIN_ID
import re
import sqlite3

from funcs.db import check_existing_user, add_new_user, log_request, get_type_id, get_photo_paths_for_establishment, get_establishment_by_id, get_places_from_db, log_booking
from funcs.openai_helper import get_gpt_recommendations, init_context_db
from keyboards.main_menu_kb import get_start_kb, get_category_kb, get_cuisine_kb, get_after_places_kb, get_back_to_start_kb
from essentials import bot

form_router = Router()

# Клавиатура для этапа ввода адреса
address_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back_to_cuisine")],
    [InlineKeyboardButton(text="Начать все заново", callback_data="restart_category")],
])

book_kb = lambda idx: InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Забронировать", callback_data=f"book_{idx}")]
])

more_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="еще заведения", callback_data="more_places")]
])

booking_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть политику конфиденциальности", callback_data="show_privacy")]
])

class BookingForm(StatesGroup):
    waiting_for_booking_info = State()

@form_router.message(Command("start"))
async def command_start(message: Message) -> None:
    await log_request(message.from_user.id)

    user_id = message.from_user.id
    start_photo = FSInputFile("start_image.JPG")

    existing_user = await check_existing_user(user_id)

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
        await add_new_user(user_id)

@form_router.callback_query(F.data.in_({"back_to_main_menu"}))
async def process_back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(f'Главное меню:',
                                           reply_markup=get_start_kb())
    await log_request(callback_query.from_user.id)

@form_router.callback_query(F.data == "best_place")
async def process_best_place(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_category_kb()
    )

@form_router.callback_query(F.data.in_({"cat_heart", "cat_gastro", "cat_romance", "cat_biz", "cat_stories"}))
async def process_category(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(category=callback_query.data)
    await callback_query.message.edit_text(
        "Выберите кухню:",
        reply_markup=get_cuisine_kb()
    )

@form_router.callback_query(F.data.in_({
    "cuisine_russian", "cuisine_italian", "cuisine_georgian", "cuisine_greek", "cuisine_asian", "cuisine_any"
}))
async def process_cuisine(callback_query: CallbackQuery, state: FSMContext):
    category = (await state.get_data()).get("category")
    cuisine = callback_query.data.replace('cuisine_', '')
    
    all_places = await get_places_from_db(category, cuisine)
    if not all_places:
        await callback_query.message.answer("Нет заведений по выбранным фильтрам.", reply_markup=get_category_kb())
        return

    await callback_query.message.edit_text("Подбираю лучшие места...")
    sorted_names = await get_gpt_recommendations(all_places, category, cuisine, callback_query.from_user.id)
    print("Ответ от GPT:", sorted_names)
    
    places_map = {place['name']: place for place in all_places}

    await state.update_data(sorted_names=sorted_names, places_map=places_map, current_index=0)
    
    await show_place(callback_query.message, state)

@form_router.callback_query(F.data == "restart_category")
async def restart_category(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_category_kb()
    )

@form_router.callback_query(F.data == "show_privacy")
async def show_privacy_policy(callback_query: CallbackQuery):
    try:
        policy_file = FSInputFile("privacy_policy.pdf")
        await callback_query.message.answer_document(
            document=policy_file,
            caption="Политика в отношении обработки персональных данных"
        )
    except Exception as e:
        await callback_query.message.answer("Извините, не удалось загрузить политику конфиденциальности.")
    await callback_query.answer()

@form_router.message(BookingForm.waiting_for_booking_info)
async def process_booking_info(message: Message, state: FSMContext):
    text = message.text
    phone_ok = bool(re.search(r"\+?\d{10,15}", text))
    if not phone_ok:
        await message.answer("Проверьте, что вы указали корректный телефон!")
        return
    data = await state.get_data()
    place = data.get("selected_place")
    place_info = f"\n\nЗаведение: {place['name']}\n{place['desc']}\n{place['address']}" if place else ""
    for admin in ADMIN_ID:
        await message.bot.send_message(admin, f"Новая бронь от пользователя @{message.from_user.username or message.from_user.id}:\n{text}{place_info}")
    
    if place:
        await log_booking(place['id'], message.from_user.id, message.text)

    await message.answer("Спасибо! Ваша заявка отправлена. Мы свяжемся с вами, если всё ок.", reply_markup=get_back_to_start_kb())
    await state.clear()

@form_router.callback_query(F.data == "more_places")
async def more_places(callback_query: CallbackQuery, state: FSMContext):
    await show_place(callback_query.message, state)

@form_router.callback_query(F.data.regexp(r"^book_(\d+)$"))
async def start_booking(callback_query: CallbackQuery, state: FSMContext):
    establishment_id = int(callback_query.data.split('_')[1])
    place = await get_establishment_by_id(establishment_id)
    if not place:
        await callback_query.answer("Извините, это заведение не найдено.", show_alert=True)
        return

    await state.update_data(selected_place=place)
    await state.set_state(BookingForm.waiting_for_booking_info)
    await callback_query.message.answer(
        "Отправь имя (или ник), телефон, время для бронирования и ник в тг, с кем можно связаться, если все столики будут заняты.\n\n"
        "Пример: Иван, +79991234567, 19:00, @ivan\n\n"
        "Отправляя свои данные, вы соглашаетесь с политикой в отношении обработки персональных данных.",
        reply_markup=booking_kb
    )
    await callback_query.answer()

async def show_place(message, state: FSMContext):
    data = await state.get_data()
    sorted_names = data.get("sorted_names", [])
    places_map = data.get("places_map", {})
    current_index = data.get("current_index", 0)

    if current_index >= len(sorted_names):
        await message.answer("Больше заведений по этим фильтрам нет.", reply_markup=get_category_kb())
        return

    place_name = sorted_names[current_index]
    place_details = places_map.get(place_name)

    if not place_details:
        await state.update_data(current_index=current_index + 1)
        await show_place(message, state)
        return
    
    establishment_text = f"{place_details['name']}\n\n{place_details['feature']}\n\n📍 {place_details['address']}\nⓂ️ {place_details['metro']}\n\n{place_details['desc']}"
    photo_paths = await get_photo_paths_for_establishment(place_details['id'])
    chat_id = message.chat.id
    
    if photo_paths:
        if len(photo_paths) == 1:
            await bot.send_photo(
                chat_id=chat_id,
                photo=FSInputFile(photo_paths[0]),
                caption=establishment_text,
                reply_markup=get_after_places_kb(place_details['id'])
            )
        else:
            media_group = MediaGroupBuilder(caption=establishment_text)
            for photo_path in photo_paths:
                media_group.add(type="photo", media=FSInputFile(photo_path))
            await bot.send_media_group(chat_id=chat_id, media=media_group.build())
            await bot.send_message(chat_id, "Что думаешь?", reply_markup=get_after_places_kb(place_details['id']))
    else:
        await bot.send_message(chat_id, establishment_text, reply_markup=get_after_places_kb(place_details['id']))

    await state.update_data(current_index=current_index + 1)

