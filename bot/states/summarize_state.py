from aiogram.fsm.state import State, StatesGroup

class SummarizeStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_level = State()
    processing = State()
    waiting_for_format = State()

