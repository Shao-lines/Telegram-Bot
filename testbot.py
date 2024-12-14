import unittest
from unittest.mock import patch, MagicMock
from bot import (
    get_country_language,
    translate_city_name,
    get_timezone,
    get_city_info,
    get_weather,
    get_country_code,
    get_currency_by_country
)

class TestBotFunctions(unittest.TestCase):

    def test_get_country_language(self):
        self.assertEqual(get_country_language("Russia"), "Русский")
        self.assertEqual(get_country_language("United States"), "Английский")
        self.assertEqual(get_country_language("Unknown Country"), "Неизвестно")

    def test_translate_city_name(self):
        self.assertEqual(translate_city_name("Москва"), "Moscow")
        self.assertEqual(translate_city_name("Киев"), "Kyiv")
        self.assertEqual(translate_city_name("UnknownCity"), "UnknownCity")

    @patch('bot.TimezoneFinder.timezone_at', return_value="Europe/Moscow")
    def test_get_timezone_valid(self, mock_timezone):
        self.assertEqual(get_timezone(55.7558, 37.6173), "Europe/Moscow")

    @patch('bot.TimezoneFinder.timezone_at', return_value=None)
    def test_get_timezone_invalid(self, mock_timezone):
        self.assertEqual(get_timezone(0, 0), "Неизвестно")

    # Мокируем translate_city_name
    @patch('deep_translator.GoogleTranslator.translate')
    def test_translate_city_name_with_mock(self, mock_translate):
        mock_translate.return_value = "Moscow"  # Возвращаем строку, а не MagicMock
        result = translate_city_name("Москва")
        self.assertEqual(result, "Moscow")

    # Мок для get_city_info (успешный запрос)
    @patch('bot.requests.get')
    def test_get_city_info_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"city": "Moscow", "country": "Russia", "latitude": 55.7558, "longitude": 37.6173}]
        }
        mock_get.return_value = mock_response
        city_info, error = get_city_info("Moscow")
        self.assertIsNone(error)
        self.assertEqual(city_info["country"], "Russia")

    # Мок для get_city_info (город не найден)
    @patch('bot.requests.get')
    def test_get_city_info_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        city_info, error = get_city_info("UnknownCity")
        self.assertIsNone(city_info)
        self.assertEqual(error, "Город 'UnknownCity' не найден.")

    # Мок для get_weather (успешный запрос)
    @patch('bot.requests.get')
    def test_get_weather_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 10},
            "weather": [{"description": "Clear sky"}]
        }
        mock_get.return_value = mock_response
        weather_info, error = get_weather("Moscow")
        self.assertIsNone(error)
        self.assertEqual(weather_info["temp"], 10)
        self.assertEqual(weather_info["desc"], "Clear sky")

    # Мок для get_weather (не удалось получить данные)
    @patch('bot.requests.get')
    def test_get_weather_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        weather_info, error = get_weather("UnknownCity")
        self.assertIsNone(weather_info)
        self.assertEqual(error, "Не удалось получить данные о погоде.")

    @patch('bot.requests.get')
    def test_get_country_code(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"countryCode": "RU"}
        mock_get.return_value = mock_response
        country_code = get_country_code("Russia")
        self.assertEqual(country_code, "RU")

    @patch('bot.requests.get')
    def test_get_currency_by_country(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"currencyCode": "RUB"}
        mock_get.return_value = mock_response
        currency = get_currency_by_country("Russia")
        self.assertEqual(currency, "RUB")
        self.assertEqual(get_currency_by_country("United States"), "USD")
        self.assertEqual(get_currency_by_country("UnknownCountry"), "Неизвестная валюта")


if __name__ == '__main__':
    unittest.main()
