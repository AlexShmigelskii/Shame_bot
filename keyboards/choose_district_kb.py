from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_district_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Арбат", callback_data="Арбат")],
        [InlineKeyboardButton(text="Басманный", callback_data="Басманный")],
        [InlineKeyboardButton(text="Замоскворечье", callback_data="Замоскворечье")],
        [InlineKeyboardButton(text="Красносельский", callback_data="Красносельский")],
        [InlineKeyboardButton(text="Мещанский", callback_data="Мещанский")],
        [InlineKeyboardButton(text="Пресненский", callback_data="Пресненский")],
        [InlineKeyboardButton(text="Таганский", callback_data="Таганский")],
        [InlineKeyboardButton(text="Тверской", callback_data="Тверской")],
        [InlineKeyboardButton(text="Хамовники", callback_data="Хамовники")],
        [InlineKeyboardButton(text="Якиманка", callback_data="Якиманка")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]
    ])
    return kb


def get_place_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ресторан", callback_data="Ресторан"),
         InlineKeyboardButton(text="Бар", callback_data="Бар")],
        [InlineKeyboardButton(text="Назад", callback_data="choose_district")],
    ])
    return kb


def get_subscription_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово!", callback_data="check_subscription")],
    ])
    return kb
