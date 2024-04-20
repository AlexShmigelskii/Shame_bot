from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    Name = State()
    Features = State()
    Address = State()
    Metro = State()
    Description = State()
    Photo = State()
