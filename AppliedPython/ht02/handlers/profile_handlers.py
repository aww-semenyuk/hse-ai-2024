from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import USERS_INFO
from states import ProfileForm
from utils import get_current_weather, calculate_calories_goal, calculate_water_goal

router = Router()

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await message.answer("Как вас называть?")
    await state.set_state(ProfileForm.name)

@router.message(ProfileForm.name)
async def name_set(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Приятно познакомиться, {message.text}! Давайте заполним ваш профиль\n\n"
                          "Укажите свой вес (кг, целое число)")
    await state.set_state(ProfileForm.weight)

@router.message(ProfileForm.weight)
async def weight_set(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
    except ValueError:
        await message.answer("Ошибка: вес должен быть целым числом")
        return
    
    await state.update_data(weight=weight)

    await message.answer("Укажите свой рост (см, целое число)")
    await state.set_state(ProfileForm.height)

@router.message(ProfileForm.height)
async def height_set(message: Message, state: FSMContext):
    try:
        height = int(message.text)
    except ValueError:
        await message.answer("Ошибка: рост должен быть целым числом")
        return
    
    await state.update_data(height=height)

    await message.answer("Укажите свой возраст (полных лет)")
    await state.set_state(ProfileForm.age)

@router.message(ProfileForm.age)
async def age_set(message: Message, state: FSMContext):
    try:
        age = int(message.text)
    except ValueError:
        await message.answer("Ошибка: возраст должен быть целым числом")
        return
    
    await state.update_data(age=age)

    await message.answer("Где вы находитесь? Укажите город")
    await state.set_state(ProfileForm.city)

@router.message(ProfileForm.city)
async def city_set(message: Message, state: FSMContext):
    await state.update_data(city=message.text)

    await message.answer("Сколько минут активности у вас в день?")
    await state.set_state(ProfileForm.daily_activity)

@router.message(ProfileForm.daily_activity)
async def activity_set(message: Message, state: FSMContext):
    try:
        daily_activity = int(message.text)
    except ValueError:
        await message.answer("Ошибка: укажите активность целым числом")
        return
    
    await state.update_data(daily_activity=daily_activity)

    await message.answer("Укажите вашу дневную цель по калориям (ккал, целое число)\n"
                         "Отправьте 'auto' для автоматического расчета")
    await state.set_state(ProfileForm.calories_goal)

@router.message(ProfileForm.calories_goal, F.text == "auto")
async def calories_set_auto(message: Message, state: FSMContext):
    data = await state.get_data()

    calories_goal = calculate_calories_goal(data["weight"], data["height"], data["age"])
    await state.update_data(calories_goal=calories_goal)

    temp = await get_current_weather(data["city"])
    water_goal = calculate_water_goal(data["weight"], data["daily_activity"], temp)
    
    USERS_INFO[message.from_user.id] = data

    USERS_INFO[message.from_user.id]["calories_goal"] = calories_goal
    USERS_INFO[message.from_user.id]["water_goal"] = water_goal

    USERS_INFO[message.from_user.id]["logged_water"] = 0
    USERS_INFO[message.from_user.id]["logged_calories"] = 0
    USERS_INFO[message.from_user.id]["burned_calories"] = 0
    
    USERS_INFO[message.from_user.id]["water_goal_base"] = water_goal
    USERS_INFO[message.from_user.id]["calories_goal_base"] = calories_goal

    await message.answer("Профиль заполнен! Теперь вы можете отслеживать свой прогресс")
    await state.clear()

@router.message(ProfileForm.calories_goal)
async def calories_set(message: Message, state: FSMContext):
    try:
        calories_goal = int(message.text)
    except ValueError:
        await message.answer("Ошибка: укажите калории целым числом или отправьте 'auto'")
        return
    
    await state.update_data(calories_goal=calories_goal)

    data = await state.get_data()
    
    temp = await get_current_weather(data["city"])
    water_goal = calculate_water_goal(data["weight"], data["daily_activity"], temp)
    
    USERS_INFO[message.from_user.id] = data

    USERS_INFO[message.from_user.id]["water_goal"] = water_goal
    
    USERS_INFO[message.from_user.id]["logged_water"] = 0
    USERS_INFO[message.from_user.id]["logged_calories"] = 0
    USERS_INFO[message.from_user.id]["burned_calories"] = 0

    USERS_INFO[message.from_user.id]["water_goal_base"] = water_goal
    USERS_INFO[message.from_user.id]["calories_goal_base"] = calories_goal

    await message.answer("Профиль заполнен! Теперь вы можете отслеживать свой прогресс")
    await state.clear()
