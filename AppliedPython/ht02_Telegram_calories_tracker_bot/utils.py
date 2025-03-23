import aiohttp
import math
from googletrans import Translator

from config import OPENWEATHER_APPID, OPENWEATHER_BASEURL, EDAMAM_APPID, EDAMAM_APPKEY, EDAMAM_BASEURL, APININJAS_APIKEY, APININJAS_BASEURL

def calculate_calories_goal(weight: int, height: int, age: int):
    return int(10*weight + 6.25*height + 5*age)

def calculate_water_goal(weight: int, daily_activity: int, temperature: float):
    return 30*weight + math.floor(daily_activity / 30)*500 + (500 if temperature is not None and temperature > 25 else 0)

def get_progress_msg(user_data: dict) -> str:
    msg_water = (f'Вода:\n'
                 f'- Выпито: {user_data["logged_water"]}/{user_data["water_goal"]} мл\n')
    if user_data["water_goal"]-user_data["logged_water"] <= 0:
        msg_water += f'- Цель по воде на данный момент выполнена'
    else:
        msg_water += f'- Осталось: {user_data["water_goal"]-user_data["logged_water"]} мл'

    msg_calories = (f'Калории:\n'
                    f'- Потреблено: {user_data["logged_calories"]}/{user_data["calories_goal"]} ккал\n'
                    f'- Сожжено: {user_data["burned_calories"]} ккал\n'
                    f'- Баланс: {user_data["logged_calories"]-user_data["burned_calories"]} ккал')

    return ("Текущий прогресс:\n\n"
            f"{msg_water}\n\n"
            f"{msg_calories}")

async def google_translate(msg: str):
    translator = Translator()
    translated = await translator.translate(msg)
    return translated.text

async def get_current_weather(city):
    city_en = await google_translate(city)

    params = {"q": city_en, "appid": OPENWEATHER_APPID, "units": "metric", "mode": "json"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(OPENWEATHER_BASEURL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    return temp
                else:
                    print(f"API Error: {response.status}, {await response.text()}")
        except aiohttp.ClientError as e:
            print(f"Client Error: {e}")

    return None

async def get_calories_burned(activity: str, duration: int):
    activity_en = await google_translate(activity)

    params = {"activity": activity_en, "duration": duration}
    headers={"X-Api-Key": APININJAS_APIKEY}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(APININJAS_BASEURL, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0]["total_calories"]
                else:
                    print(f"API Error: {response.status}, {await response.text()}")
        except aiohttp.ClientError as e:
            print(f"Client Error: {e}")

    return None

async def get_food_calories(food: str, weight: int):
    food_en = await google_translate(food)

    params={"app_id": EDAMAM_APPID, "app_key": EDAMAM_APPKEY, "ingr": f"{food_en} {weight}g"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(EDAMAM_BASEURL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["calories"]
                else:
                    print(f"API Error: {response.status}, {await response.text()}")
        except aiohttp.ClientError as e:
            print(f"Client Error: {e}")

    return None
