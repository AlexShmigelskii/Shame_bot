from aiogram.fsm.state import StatesGroup, State


class Add_Form(StatesGroup):
    Name = State()
    Features = State()
    Address = State()
    Metro = State()
    Description = State()
    Photo = State()


class Delete_Form(StatesGroup):
    EstablishmentNumber = State()


class Stats_Form(StatesGroup):
    Period = State()
