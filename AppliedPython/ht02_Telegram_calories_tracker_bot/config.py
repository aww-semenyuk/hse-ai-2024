import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_APPID = os.getenv("OPENWEATHER_API_APPID")
EDAMAM_APPID = os.getenv("EDAMAM_API_APPID")
EDAMAM_APPKEY = os.getenv("EDAMAM_API_APPKEY")
APININJAS_APIKEY = os.getenv("APININJAS_API_KEY")

OPENWEATHER_BASEURL = "https://api.openweathermap.org/data/2.5/weather"
EDAMAM_BASEURL = "https://api.edamam.com/api/nutrition-data"
APININJAS_BASEURL = "https://api.api-ninjas.com/v1/caloriesburned"

USERS_INFO = {}
