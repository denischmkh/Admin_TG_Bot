from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    in_chat = State()
    in_menu = State()