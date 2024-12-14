import logging
import requests
from telegram import Update
from deep_translator import GoogleTranslator
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from geopy.geocoders import Nominatim
import time
from timezonefinder import TimezoneFinder
import pycountry

def get_timezone_with_delay(lat, lon):
    """Получает часовой пояс с задержкой 1 секунду для предотвращения превышения лимита запросов.

    Args:
        lat (float): Широта.
        lon (float): Долгота.

    Returns:
        str: Название часового пояса.
    """
    time.sleep(1)  # Добавляем задержку 1 секунду между запросами
    return get_timezone(lat, lon)


# Конфигурация
TELEGRAM_TOKEN = '7911202258:AAFWEpumhc1L0wsm6LUZm2SlZMsZEz_l_NQ'
WEATHER_API_KEY = '4daca21a275194cb5e7f9173fed66205'
GEO_API_KEY = '12dfdc0a44mshb825a226435bbcep17b219jsn55cccc68b02b'
GOOGLE_API_KEY = "AIzaSyBQf00MJqLk3vqUM6gSQBtWvsMaNx-tB7Y"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Словарь для определения языка по стране
country_languages = {
    "Russia": "Русский",
    "Ukraine": "Украинский",
    "United States": "Английский",
    "Kazakhstan": "",
    "France": "Французский",
    "Germany": "Немецкий",
    "Spain": "Испанский",
    "Italy": "Итальянский",
    "Japan": "Японский",
    "China": "Китайский",
    "India": "Хинди",
    "Brazil": "Португальский",
    "Portugal": "Португальский",
    "Belize": "Английский",
    "People's Republic of China": "Китайский",
    "United Arab Emirates": "Английский,Арабский"
}


def get_country_language(country_name):
    """Определяет язык для заданной страны.

    Args:
        country_name (str): Название страны.

    Returns:
        str: Язык, говоримый в стране.
    """
    return country_languages.get(country_name, "Неизвестно")


def translate_city_name(city_name):
    """Переводит название города с русского на английский.

    Args:
        city_name (str): Название города на русском языке.

    Returns:
        str: Переведенное название города.
    """
    try:
        translated = GoogleTranslator(source='ru', target='en').translate(city_name)
        return translated
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return city_name  # Если перевод не удался, возвращаем оригинальное название


def get_timezone(lat, lon):
    """Определяет часовой пояс для заданных координат.

    Args:
        lat (float): Широта.
        lon (float): Долгота.

    Returns:
        str: Название часового пояса.
    """
    try:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lon)
        if tz_name:
            return tz_name
        return "Неизвестно"
    except Exception as e:
        print(f"Ошибка определения часового пояса: {e}")
        return "Неизвестно"


def get_city_info(city_name):
    """Получает информацию о городе: страну, часовой пояс, язык и координаты.

    Args:
        city_name (str): Название города.

    Returns:
        dict: Информация о городе, включая страну, часовой пояс, язык и координаты.
        str: Сообщение об ошибке в случае неудачи.
    """
    city_name_en = translate_city_name(city_name)

    geo_url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
    headers = {"X-RapidAPI-Key": GEO_API_KEY}
    params = {"namePrefix": city_name_en, "limit": 10}

    try:
        response = requests.get(geo_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if not data['data']:
            return None, f"Город '{city_name}' не найден."

        for city in data['data']:
            if city['city'].lower() == city_name_en.lower():
                # Коррекция для Москвы
                if city_name_en.lower() == "moscow" and city['country'] != "Russia":
                    city['country'] = "Russia"

                lat = city.get("latitude")
                lon = city.get("longitude")
                tz = get_timezone(lat, lon) if lat and lon else "Неизвестно"

                country_language = get_country_language(city["country"])
                return {
                    "city": city["city"],
                    "country": city["country"],
                    "timezone": tz,
                    "language": country_language
                }, None

        return None, f"Точный город '{city_name}' не найден, возможно, вы имели в виду другой."
    except requests.exceptions.RequestException as e:
        return None, f"Ошибка API: {e}"


def get_weather(city_name):
    """Получает погоду для города.

    Args:
        city_name (str): Название города.

    Returns:
        dict: Информация о погоде, включая температуру и описание погоды.
        str: Сообщение об ошибке в случае неудачи.
    """
    city_name_en = translate_city_name(city_name)

    weather_url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name_en,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"  # Указываем русский язык для описания погоды
    }
    response = requests.get(weather_url, params=params)
    if response.status_code != 200:
        return None, "Не удалось получить данные о погоде."
    weather_data = response.json()
    weather_info = {
        "temp": weather_data["main"]["temp"],
        "desc": weather_data["weather"][0]["description"]
    }
    return weather_info, None


def get_country_code(country_name):
    """Получает двухбуквенный код страны по ее названию.

    Args:
        country_name (str): Название страны.

    Returns:
        str: Двухбуквенный код страны.
    """
    try:
        country = pycountry.countries.get(name=country_name)
        if country:
            return country.alpha_2  # Возвращаем двухбуквенный код страны
        return None
    except Exception as e:
        print(f"Ошибка получения кода страны: {e}")
        return None


def get_currency_by_country(country_name):
    """Получает валюту для заданной страны.

    Args:
        country_name (str): Название страны.

    Returns:
        str: Валюта, используемая в стране.
    """
    country_code_map = {
        "Russia": "RU",
        "United States": "US",
        "France": "FR",
        "Germany": "DE",
        "Japan": "JP",
        "India": "IN",
        "United Kingdom": "GB",
        "China": "CN",
        "People's Republic of China": "CN",
        "Brazil": "BR",
        "Italy": "IT",
        "Spain": "ES",
        "Portugal": "PT",
        "Belize": "BZ",
        "United Arab Emirates": "AE"
    }

    country_code = country_code_map.get(country_name, country_name)

    currency_dict = {
        "RU": "RUB",  # Россия — рубль
        "US": "USD",  # США — доллар
        "FR": "EUR",  # Франция — евро
        "DE": "EUR",  # Германия — евро
        "JP": "JPY",  # Япония — иена
        "IN": "INR",  # Индия — рупия
        "GB": "GBP",  # Великобритания — фунт
        "CN": "CNY",  # Китай — юань
        "BR": "BRL",  # Бразилия — реал
        "IT": "EUR",  # Италия — евро
        "ES": "EUR",  # Испания — евро
        "PT": "EUR",  # Португалия — евро
        "BZ": "BZD",  # Белиз — белизский доллар
        "AE": "AED"   # ОАЭ — дирхам
    }

    return currency_dict.get(country_code.upper(), "Неизвестная валюта")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start, отправляет приветственное сообщение.

    Args:
        update (telegram.Update): Обновление, содержащее информацию о сообщении.
        context (telegram.ext.CallbackContext): Контекст для обработки команды.
    """
    await update.message.reply_text(
        "Привет! Введите название города, и я предоставлю информацию о нем."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщение пользователя, получая информацию о городе.

    Args:
        update (telegram.Update): Обновление, содержащее информацию о сообщении.
        context (telegram.ext.CallbackContext): Контекст для обработки команды.
    """
    city_name = update.message.text  # Город, который отправил пользователь

    # Получаем данные о городе
    city_info, city_error = get_city_info(city_name)
    if city_error:
        await update.message.reply_text(city_error)
        return

    # Получаем данные о погоде
    weather_info, weather_error = get_weather(city_name)
    if weather_error:
        await update.message.reply_text(weather_error)
        return

    currency = get_currency_by_country(city_info['country'])

    # Формируем ответ
    response = (
        f"Информация о городе {city_info['city']}:\n"
        f"Страна: {city_info['country']}\n"
        f"Часовой пояс: {city_info['timezone']}\n"
        f"Температура: {weather_info['temp']}°C\n"
        f"Погода: {weather_info['desc']}\n"
        f"Язык: {city_info['language']}\n"
        f"Валюта: {currency}\n"
    )
    await update.message.reply_text(response)


# Основной запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен!")
    app.run_polling()
