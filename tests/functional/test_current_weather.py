import pytest
import re

"""pytest tests/functional/test_current_weather.py -v"""
class TestCurrentWeatherFunctional:
    """Функциональные тесты GET /data/2.5/weather"""

    @pytest.mark.functional
    def test_basic_request_by_coordinates(self, api_client):
        """W-F-01: Базовый запрос по координатам (Москва)."""
        response = api_client.get_current_weather(lat=55.75, lon=37.62)

        assert response.status_code == 200

        data = response.json()
        assert data["cod"] == 200
        assert "coord" in data
        assert "weather" in data
        assert "main" in data
        assert "wind" in data
        assert data["name"] == "Moscow"

    @pytest.mark.functional
    def test_units_metric(self, api_client):
        """W-F-02: units=metric, температура в Цельсиях."""
        response = api_client.get_current_weather(
            lat=51.51, lon=-0.13, units="metric"
        )
        assert response.status_code == 200

        temp = response.json()["main"]["temp"]
        assert -90 <= temp <= 60, f"Температура {temp}°C вне разумного диапазона"

    @pytest.mark.functional
    def test_units_imperial(self, api_client):
        """W-F-03: units=imperial, температура в Фаренгейтах."""
        response = api_client.get_current_weather(
            lat=51.51, lon=-0.13, units="imperial"
        )
        assert response.status_code == 200

        temp = response.json()["main"]["temp"]
        assert -130 <= temp <= 140, f"Температура {temp}°F вне разумного диапазона"

    @pytest.mark.functional
    def test_units_standard_default(self, api_client):
        """W-F-04: Без units — температура в Кельвинах."""
        response = api_client.get_current_weather(lat=51.51, lon=-0.13)
        assert response.status_code == 200

        temp = response.json()["main"]["temp"]
        assert temp > 170, f"Температура {temp}K слишком низкая для Кельвинов"

    @pytest.mark.functional
    def test_lang_ru(self, api_client):
        """W-F-05: lang=ru, описание на кириллице."""
        response = api_client.get_current_weather(
            lat=55.75, lon=37.62, lang="ru"
        )
        assert response.status_code == 200

        description = response.json()["weather"][0]["description"]
        assert re.search(r"[а-яА-ЯёЁ]", description), (
            f"Описание '{description}' не содержит кириллицу"
        )

    @pytest.mark.functional
    def test_lang_ja(self, api_client):
        """W-F-06: lang=ja, описание на японском."""
        response = api_client.get_current_weather(
            lat=35.68, lon=139.69, lang="ja"
        )
        assert response.status_code == 200

        description = response.json()["weather"][0]["description"]
        assert re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", description), (
            f"Описание '{description}' не содержит японские символы"
        )

    @pytest.mark.functional
    def test_lang_en(self, api_client):
        """W-F-07: lang=en, описание на латинице."""
        response = api_client.get_current_weather(
            lat=51.51, lon=-0.13, lang="en"
        )
        assert response.status_code == 200

        description = response.json()["weather"][0]["description"]
        assert re.search(r"[a-zA-Z]", description), (
            f"Описание '{description}' не содержит латиницу"
        )

    @pytest.mark.functional
    def test_mode_xml(self, api_client):
        """W-F-08: mode=xml возвращает XML."""
        response = api_client.get_current_weather(
            lat=51.51, lon=-0.13, mode="xml"
        )
        assert response.status_code == 200
        assert "xml" in response.headers.get("Content-Type", "").lower()
        assert response.text.strip().startswith("<")

    @pytest.mark.functional
    def test_deprecated_query_by_city_name(self, api_client):
        """W-F-09: Deprecated запрос по q=London."""
        response = api_client.get_current_weather(q="London")
        assert response.status_code == 200
        assert response.json()["name"] == "London"

    @pytest.mark.functional
    def test_deprecated_query_by_zip(self, api_client):
        """W-F-10: Deprecated запрос по zip=10001,US."""
        response = api_client.get_current_weather(zip="10001,US")
        assert response.status_code == 200

        data = response.json()
        assert data["sys"]["country"] == "US"