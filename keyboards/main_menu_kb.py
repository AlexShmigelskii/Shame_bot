from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбор заведения", callback_data='best_place')],
    ])
    return kb


def get_category_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Душевно и вкусно", callback_data='cat_heart')],
        [InlineKeyboardButton(text="Гастрономический экстаз", callback_data='cat_gastro')],
        [InlineKeyboardButton(text="Романтика", callback_data='cat_romance')],
        [InlineKeyboardButton(text="Бизнес и нетворкинг", callback_data='cat_biz')],
        [InlineKeyboardButton(text="Получить 🔥 на сторис", callback_data='cat_stories')],
        [InlineKeyboardButton(text="Назад", callback_data='back_to_main_menu')],
    ])
    return kb


def get_cuisine_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русская", callback_data='cuisine_russian')],
        [InlineKeyboardButton(text="Итальянская", callback_data='cuisine_italian')],
        [InlineKeyboardButton(text="Грузинская", callback_data='cuisine_georgian')],
        [InlineKeyboardButton(text="Греческая", callback_data='cuisine_greek')],
        [InlineKeyboardButton(text="Азиатская", callback_data='cuisine_asian')],
        [InlineKeyboardButton(text="Без разницы", callback_data='cuisine_any')],
        [InlineKeyboardButton(text="Начать всё заново", callback_data='restart_category')],
    ])
    return kb


def get_after_places_kb(establishment_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Забронировать", callback_data=f"book_{establishment_id}")],
        [InlineKeyboardButton(text="Ещё заведения", callback_data="more_places")],
        [InlineKeyboardButton(text="Начать всё заново", callback_data="restart_category")],
    ])
    return kb


def get_back_to_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="К началу", callback_data="back_to_main_menu")]
    ])
    return kb
