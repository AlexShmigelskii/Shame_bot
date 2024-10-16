from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить", callback_data="add"),
         InlineKeyboardButton(text="Удалить", callback_data="delete")],
        [InlineKeyboardButton(text="Вывести статистику", callback_data="show_stats")]
    ])
    return kb


def get_admin_district_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Арбат", callback_data="admin_Арбат")],
        [InlineKeyboardButton(text="Басманный", callback_data="admin_Басманный")],
        [InlineKeyboardButton(text="Замоскворечье", callback_data="admin_Замоскворечье")],
        [InlineKeyboardButton(text="Красносельский", callback_data="admin_Красносельский")],
        [InlineKeyboardButton(text="Мещанский", callback_data="admin_Мещанский")],
        [InlineKeyboardButton(text="Пресненский", callback_data="admin_Пресненский")],
        [InlineKeyboardButton(text="Таганский", callback_data="admin_Таганский")],
        [InlineKeyboardButton(text="Тверской", callback_data="admin_Тверской")],
        [InlineKeyboardButton(text="Хамовники", callback_data="admin_Хамовники")],
        [InlineKeyboardButton(text="Якиманка", callback_data="admin_Якиманка")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_admin")]
    ])
    return kb


def get_admin_place_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ресторан", callback_data="admin_Ресторан"),
         InlineKeyboardButton(text="Бар", callback_data="admin_Бар")],
    ])
    return kb


def get_admin_stop_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово!", callback_data="photos_done")],
    ])
    return kb


def back_to_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отлично!", callback_data="back_to_admin")],
    ])
    return kb


def back_to_admin_after_stats_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отлично!", callback_data="back_to_admin_after_stats")],
    ])
    return kb


def nothing_to_show_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад!", callback_data="back_to_admin")],
    ])
    return kb
