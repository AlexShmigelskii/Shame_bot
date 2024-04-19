from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать район", callback_data='choose_district')],
    ])
    return kb
