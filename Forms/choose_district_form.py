from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    is_subscriber = State()
    chose_district = State()
    chose_place = State()
