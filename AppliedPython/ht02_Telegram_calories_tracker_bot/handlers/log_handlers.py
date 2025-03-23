from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
import math

from utils import get_food_calories, get_calories_burned, get_progress_msg
from config import USERS_INFO
import const.text_constants as tc

router = Router()

@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    if message.from_user.id not in USERS_INFO.keys():
        await message.answer(tc.SET_PROFILE_FIRST)
        return
    
    data = USERS_INFO[message.from_user.id]
    msg = get_progress_msg(data)

    await message.answer(msg)

@router.message(Command("new_day"))
async def cmd_new_day(message: Message):
    if message.from_user.id not in USERS_INFO.keys():
        await message.answer(tc.SET_PROFILE_FIRST)
        return

    USERS_INFO[message.from_user.id]["calories_goal"] = USERS_INFO[message.from_user.id]["calories_goal_base"]
    USERS_INFO[message.from_user.id]["water_goal"] = USERS_INFO[message.from_user.id]["water_goal_base"]
    
    USERS_INFO[message.from_user.id]["logged_water"] = 0
    USERS_INFO[message.from_user.id]["logged_calories"] = 0
    USERS_INFO[message.from_user.id]["burned_calories"] = 0

    msg = get_progress_msg(USERS_INFO[message.from_user.id])

    await message.answer("Вы начали новый день!")
    await message.answer(msg)

@router.message(Command("log_water"))
async def cmd_log_water(message: Message, command: CommandObject):
    if message.from_user.id not in USERS_INFO.keys():
        await message.answer(tc.SET_PROFILE_FIRST)
        return
    if command.args is None:
        await message.answer('\n'.join([tc.PASS_ARGS, tc.LOG_WATER_EXAMPLE]),
                             parse_mode=ParseMode.MARKDOWN_V2)
        return
    try:
        logged_water = int(command.args)
    except ValueError:
        await message.answer('\n'.join([tc.WRONG_ARGS, tc.LOG_WATER_EXAMPLE]),
                             parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    USERS_INFO[message.from_user.id]["logged_water"] += logged_water

    logged = USERS_INFO[message.from_user.id]["logged_water"]
    goal = USERS_INFO[message.from_user.id]["water_goal"]

    msg = f"Выпито воды: {logged}/{goal} мл\n"
    if goal-logged <= 0:
        msg += "Отлично, цель по воде на данный момент выполнена"
    else:
        msg += f"Осталось: {goal-logged} мл"

    await message.answer(msg)

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, command: CommandObject):
    if message.from_user.id not in USERS_INFO.keys():
        await message.answer(tc.SET_PROFILE_FIRST)
        return
    if command.args is None:
        await message.answer('\n'.join([tc.PASS_ARGS, tc.LOG_FOOD_EXAMPLE]),
                             parse_mode=ParseMode.MARKDOWN_V2)
        return
    try:
        food, weight = command.args.rsplit(' ', maxsplit=1)
        weight = int(weight)
    except ValueError:
        await message.answer('\n'.join([tc.WRONG_ARGS, tc.LOG_FOOD_EXAMPLE]),
                             parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    food_calories = await get_food_calories(food, weight)
    
    USERS_INFO[message.from_user.id]["logged_calories"] += food_calories

    await message.answer(f"Записано: {food_calories} ккал")

@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, command: CommandObject):
    if message.from_user.id not in USERS_INFO.keys():
        await message.answer(tc.SET_PROFILE_FIRST)
        return
    if command.args is None:
        await message.answer('\n'.join([tc.PASS_ARGS, tc.LOG_WORKOUT_EXAMPLE]),
                             parse_mode=ParseMode.MARKDOWN_V2)
        return
    try:
        workout_type, duration = command.args.rsplit(' ', maxsplit=1)
        duration = int(duration)
    except ValueError:
        await message.answer('\n'.join([tc.WRONG_ARGS, tc.LOG_WORKOUT_EXAMPLE]),
                             parse_mode=ParseMode.MARKDOWN_V2)
        return
    
    burned_calories = await get_calories_burned(workout_type, duration)
    additional_water = math.floor(duration / 30)*200

    USERS_INFO[message.from_user.id]["water_goal"] += additional_water
    USERS_INFO[message.from_user.id]["burned_calories"] += burned_calories

    msg = f"На тренировке вы сожгли {burned_calories} ккал"
    if additional_water > 0:
        msg += f"\nВыпейте {additional_water} мл воды дополнительно (добавлено в цель)"

    await message.answer(msg)
