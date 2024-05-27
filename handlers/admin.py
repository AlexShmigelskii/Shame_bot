import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd

import datetime

from Forms.admin_form import Add_Form, Delete_Form, Stats_Form

from keyboards.admin_kb import get_admin_kb, get_admin_district_kb, get_admin_place_kb, get_admin_stop_kb, \
    back_to_admin_kb, nothing_to_show_kb, back_to_admin_after_stats_kb

from funcs.db import get_district_id, get_type_id, save_establishment_to_database, check_existing_establishment, \
    save_photo_path_to_database, get_establishments_any_type, delete_establishment, \
    get_user_count, get_establishment_count, get_request_counts_by_hour

from secret import ADMIN_ID

from essentials import bot

form_router = Router()


async def is_admin(user_id):
    # Проверка в локальном списке администраторов
    if user_id in ADMIN_ID:
        return True

    try:
        # Получение списка администраторов чата
        chat_admins = await bot.get_chat_administrators(chat_id='@shamemedia')
        chat_admin_ids = [admin.user.id for admin in chat_admins]

        # Проверка, является ли пользователь администратором чата
        if user_id in chat_admin_ids:
            return True
    except Exception as e:
        print(f"Ошибка при получении списка администраторов чата: {e}")

    return False


@form_router.message(Command("admin"))
async def command_admin(message: Message) -> None:
    # Проверяем, является ли отправитель администратором
    if await is_admin(message.from_user.id):

        num_user = get_user_count()
        num_establishments = get_establishment_count()

        # Отправляем сообщение о входе в режим администратора
        await message.answer("Вы вошли в режим администратора."
                             f"\nВсего пользователей: {num_user}"
                             f"\nВсего заведений: {num_establishments}",
                             reply_markup=get_admin_kb())

    else:
        await message.answer("У вас нет прав доступа к этой функции.")


@form_router.callback_query(F.data.in_({"back_to_admin"}))
async def process_back_to_admin(callback_query: CallbackQuery):
    num_user = get_user_count()
    num_establishments = get_establishment_count()

    await callback_query.message.edit_text("Административная панель:"
                                           f"\nВсего пользователей:{num_user}"
                                           f"\nВсего заведений:{num_establishments}",
                                           reply_markup=get_admin_kb())


@form_router.callback_query(F.data.in_({"back_to_admin_after_stats"}))
async def process_back_to_admin_after_stats(callback_query: CallbackQuery):
    num_user = get_user_count()
    num_establishments = get_establishment_count()

    await callback_query.message.answer("Административная панель:"
                                        f"\nВсего пользователей:{num_user}"
                                        f"\nВсего заведений:{num_establishments}",
                                        reply_markup=get_admin_kb())


@form_router.callback_query(F.data.in_({"add", "delete"}))
async def manage_district(callback_query: CallbackQuery, state: FSMContext):
    option_chosen = callback_query.data
    action_text = "добавляем" if option_chosen == "add" else "удаляем"

    await state.update_data(admin_action=option_chosen)
    await callback_query.message.edit_text(f"В каком районе {action_text}?",
                                           reply_markup=get_admin_district_kb())


@form_router.callback_query(F.data.in_({"admin_Арбат", "admin_Басманный",
                                        "admin_Замоскворечье", "admin_Красносельский",
                                        "admin_Мещанский", "admin_Пресненский",
                                        "admin_Таганский", "admin_Тверской",
                                        "admin_Хамовники", "admin_Якиманка"}))
async def process_admin_chosen_district(callback_query: CallbackQuery, state: FSMContext):
    district = callback_query.data
    await state.update_data(new_establishment_district=district)

    admin_data = await state.get_data()
    action = admin_data.get("admin_action")

    if action == "add":

        await callback_query.message.edit_text(f"Что добавляем?",
                                               reply_markup=get_admin_place_kb())

    elif action == "delete":

        establishments = await get_establishments_any_type(district)

        if establishments:
            establishments_dict = {i + 1: est[0] for i, est in enumerate(establishments)}

            # Сохраняем словарь в состояние FSM
            await state.update_data(establishments_dict=establishments_dict)

            establishments_info = "\n".join([f"{i + 1}. {est[1]}" for i, est in enumerate(establishments)])
            await callback_query.message.edit_text(
                f"Выберите номер заведения, которое хотите удалить:\n{establishments_info}")
            await state.set_state(Delete_Form.EstablishmentNumber)
        else:
            await callback_query.message.edit_text("В этом районе нет заведений для удаления.")


@form_router.callback_query(F.data.in_({"admin_Ресторан", "admin_Бар"}))
async def process_add_delete_chosen_place(callback_query: CallbackQuery, state: FSMContext):
    place = callback_query.data
    await state.update_data(new_establishment_type=place)
    admin_data = await state.get_data()
    action = admin_data.get("admin_action")

    if action == "add":
        await callback_query.message.answer("Введите название заведения:")
        await state.set_state(Add_Form.Name)  # Переход к состоянию для ввода названия заведения


@form_router.message(Add_Form.Name)
async def process_name_input(message: Message, state: FSMContext):
    establishment_name = message.text

    await state.update_data(new_establishment_name=establishment_name)
    await message.answer("Введите особенности заведения:")
    await state.set_state(Add_Form.Features)


@form_router.message(Add_Form.Features)
async def process_features_input(message: Message, state: FSMContext):
    establishment_features = message.text

    await state.update_data(new_establishment_features=establishment_features)
    await message.answer("Введите адрес заведения:")
    await state.set_state(Add_Form.Address)


@form_router.message(Add_Form.Address)
async def process_address_input(message: Message, state: FSMContext):
    establishment_address = message.text

    await state.update_data(new_establishment_address=establishment_address)
    await message.answer("Введите ближайшие станции метро:")
    await state.set_state(Add_Form.Metro)


@form_router.message(Add_Form.Metro)
async def process_metro_input(message: Message, state: FSMContext):
    metro = message.text

    await state.update_data(new_metro=metro)
    await message.answer("Введите описание:")
    await state.set_state(Add_Form.Description)


@form_router.message(Add_Form.Description)
async def process_description_input(message: Message, state: FSMContext):
    description = message.text

    await state.update_data(new_description=description)
    await message.answer("Присылай мне по одной фотографии")
    await state.set_state(Add_Form.Photo)


@form_router.message(Add_Form.Photo, F.photo)
async def process_photo_input(message: Message, state: FSMContext, PHOTOS_FOLDER="photos"):
    # Получаем идентификатор фотографии, отправленной пользователем
    photo_id = message.photo[-1].file_id

    # Сохраняем идентификатор фотографии в состоянии FSM
    await state.update_data(photo_id=photo_id)

    establishment_data = await state.get_data()
    establishment_name = establishment_data.get("new_establishment_name")
    establishment_features = establishment_data.get("new_establishment_features")
    establishment_address = establishment_data.get("new_establishment_address")
    metro = establishment_data.get("new_metro")
    description = establishment_data.get("new_description")
    establishment_type = establishment_data.get("new_establishment_type").split("_")[1]
    district = establishment_data.get("new_establishment_district").split("_")[1]

    establishment_type_id = get_type_id(establishment_type)
    district_id = get_district_id(district)

    existing_establishment_id = await check_existing_establishment(establishment_name, establishment_address,
                                                                   metro, description, establishment_type_id,
                                                                   district_id)
    if existing_establishment_id:
        establishment_id = existing_establishment_id
    else:
        # Создаем новое заведение
        establishment_id = await save_establishment_to_database(establishment_name, establishment_features,
                                                                establishment_address,
                                                                metro, description, district_id,
                                                                establishment_type_id)

    # Создаем папку для фотографий заведения, если ее нет
    photos_folder_path = os.path.join(PHOTOS_FOLDER, str(establishment_id))
    os.makedirs(photos_folder_path, exist_ok=True)

    # Определяем индекс для текущей фотографии
    index = len(os.listdir(photos_folder_path)) + 1

    # Сохраняем фотографию в папке photos/{establishment_id}
    photo_path = os.path.join(photos_folder_path, f"photo_{index}.jpg")
    await message.bot.download(photo_id, photo_path)

    # Сохраняем путь к фотографии в базу данных
    save_photo_path_to_database(establishment_id, photo_path)

    await message.answer('Фотография успешно добавлена! Можешь прислать еще одну или нажать "готово"',
                         reply_markup=get_admin_stop_kb())


@form_router.callback_query(Add_Form.Photo, F.data.in_({"photos_done"}))
async def process_state_exit(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Заведение с фотографиями загружены!",
                                        reply_markup=nothing_to_show_kb())
    await state.clear()


@form_router.message(Delete_Form.EstablishmentNumber)
async def process_number_establishment_to_delete(message: Message, state: FSMContext):
    number_to_delete = int(message.text)

    # Получаем сохраненный словарь из состояния FSM
    admin_data = await state.get_data()
    establishments_dict = admin_data.get("establishments_dict")

    # Проверяем, есть ли выбранное заведение в словаре
    establishment_id = establishments_dict.get(number_to_delete)

    if establishment_id:
        delete_establishment(establishment_id)

        await message.answer(f"Заведение с номером {number_to_delete} удалено.",
                             reply_markup=back_to_admin_kb())

        await state.clear()
    else:
        await message.answer("Неверный номер заведения.")


@form_router.callback_query(F.data.in_({"show_stats"}))
async def show_statistics_command(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("За какой срок вывести статистику? (введите количество дней)")
    days = callback_query.data
    await state.update_data(days_to_show=days)
    await state.set_state(Stats_Form.Period)


@form_router.message(Stats_Form.Period)
async def get_stats_period(message: Message, state: FSMContext):
    try:
        period = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число дней.")
        return

    end_date = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - datetime.timedelta(days=period)

    # Получение данных
    # Создание временного индекса с интервалом в час
    time_index = pd.date_range(start=start_date, end=end_date, freq='h')

    # Список hours содержит все часы между start_date и end_date
    hours = time_index.to_pydatetime().tolist()

    # Получение данных
    request_counts = get_request_counts_by_hour(start_date, end_date)

    if not request_counts:
        await message.answer("За указанный период данных нет.",
                             reply_markup=nothing_to_show_kb())
        await state.clear()
        return

    # Создание списка counts, где для каждого часа будет количество запросов или 0, если запросов не было
    counts = [request_counts.get(hour, 0) for hour in hours]

    # Построение графика
    plt.figure(figsize=(15, 7))
    plt.plot(hours, counts, marker='o')
    plt.title('Количество запросов в бот')
    plt.xlabel('Время')
    plt.ylabel('Количество запросов')
    plt.grid(True)

    # Настройка меток по оси X
    if period <= 2:
        locator = mdates.HourLocator(interval=1)
        formatter = mdates.DateFormatter('%d-%m %H:%M')
    elif period <= 7:
        locator = mdates.HourLocator(interval=6)
        formatter = mdates.DateFormatter('%d-%m %H:%M')
    elif period <= 30:
        locator = mdates.DayLocator(interval=1)
        formatter = mdates.DateFormatter('%d-%m')
    else:
        locator = mdates.DayLocator(interval=7)
        formatter = mdates.DateFormatter('%d-%m')

    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)

    plt.xticks(rotation=70)
    plt.tight_layout()

    # Путь для сохранения графика с уникальным именем
    unique_filename = f'stats_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.png'
    graph_filepath = os.path.join('photos', 'graphs', unique_filename)
    plt.savefig(graph_filepath)

    # Отправка графика администратору
    await message.answer_photo(FSInputFile(graph_filepath), caption="Статистика обработанных запросов за указанный "
                                                                    "период",
                               reply_markup=back_to_admin_after_stats_kb())

    # Удаление локального файла
    os.remove(graph_filepath)

    await state.clear()
