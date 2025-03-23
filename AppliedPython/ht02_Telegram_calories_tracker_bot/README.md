# Daily water & calories telegram bot tracker

## Основные функции

- Создание профиля, расчет индивидуальных дневных норм воды и калорий
- Учет тренировок, питания, потребления воды
- Отслеживание текущего прогресса

## Использованные API

- [Edamam Nutrition Analysis API](https://developer.edamam.com/edamam-docs-nutrition-api) - расчет энергетической ценности продуктов/блюд
- [API Ninjas Calories Burned API](https://www.api-ninjas.com/api/caloriesburned) - учет сожженных при активностях калорий
- [OpenWeather API](https://openweathermap.org/current) - получение температуры для указанной пользователем локации (участвует в расчете нормы воды)
- Google Translate API (via [googletrans](https://pypi.org/project/googletrans/) python lib) - перевод введенного пользователем текста на английский язык для использования в запросах к описанным выше API

## Демо

![screencast](media/bot_screencast.gif)
