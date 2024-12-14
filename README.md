Telegram Weather Bot

This project is a Telegram bot that provides detailed information about cities, including weather, timezone, language, and currency.

Features

Translate city names from Russian to English automatically.

Fetch weather information using the OpenWeather API.

Determine the timezone and language of the city.

Display currency used in the city.

Simple and intuitive interaction through Telegram.

Requirements

Python 3.8+

Telegram Bot Token

API keys for the following services:

OpenWeather

GeoDB

Google Cloud (for translations)

Installation

Clone this repository:

git clone https://github.com/your-repo/telegram-weather-bot.git
cd telegram-weather-bot

Install dependencies:

pip install -r requirements.txt

Create a .env file to store your API keys and tokens:

TELEGRAM_TOKEN=your_telegram_bot_token
WEATHER_API_KEY=your_openweather_api_key
GEO_API_KEY=your_geodb_api_key
GOOGLE_API_KEY=your_google_api_key

Run the bot:

python bot.py

Usage

Start the bot in Telegram by sending /start.

Enter the name of a city to get detailed information:

Country

Timezone

Current weather (temperature and description)

Language spoken in the country

Currency used

API Keys

Telegram Bot Token: Create a bot using BotFather and get the token.

OpenWeather API Key: Sign up at OpenWeather and get your API key.

GeoDB API Key: Register at RapidAPI and subscribe to the GeoDB Cities API.

Google Cloud API Key: Enable Google Cloud Translation API and get the API key.

Dependencies

The bot uses the following Python libraries:

python-telegram-bot

requests

deep-translator

geopy

timezonefinder

Install them with:

pip install python-telegram-bot requests deep-translator geopy timezonefinder

Notes

The bot includes a rate limit (1 second delay) for timezone calculations to avoid overloading the API.

This bot is partially inspired by the book Mastering Telegram Bots by Julian Laufer.

License

This project is licensed under the MIT License. See the LICENSE file for details.
