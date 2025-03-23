from aiogram.fsm.state import State, StatesGroup

class ProfileForm(StatesGroup):
    name = State()
    weight = State()
    height = State()
    age = State()
    city = State()
    daily_activity = State()
    calories_goal = State()
