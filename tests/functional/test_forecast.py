import pytest
import re

"""pytest tests/functional/test_forecast.py -v"""
class TestForecastFunctional:
    """Функциональные тесты GET /data/2.5/forecast"""

    @pytest.mark.functional
    def test_basic_request(self, api_client):
        """F-F-01: Базовый запрос, cnt=40, list из 40 элементов."""
        response = api_client.get_forecast(lat=55.75, lon=37.62)
        assert response.status_code == 200

        data = response.json()
        assert data["cnt"] == 40
        assert len(data["list"]) == 40

    @pytest.mark.functional
    def test_cnt_parameter(self, api_client):
        """F-F-02: cnt=5 ограничивает количество записей."""
        response = api_client.get_forecast(lat=55.75, lon=37.62, cnt=5)
        assert response.status_code == 200

        data = response.json()
        assert data["cnt"] == 5
        assert len(data["list"]) == 5

    @pytest.mark.functional
    def test_units_metric(self, api_client):
        """F-F-03: units=metric, температуры в Цельсиях."""
        response = api_client.get_forecast(
            lat=51.51, lon=-0.13, units="metric", cnt=1
        )
        assert response.status_code == 200

        temp = response.json()["list"][0]["main"]["temp"]
        assert -90 <= temp <= 60, f"Температура {temp}°C вне разумного диапазона"

    @pytest.mark.functional
    def test_lang_ru(self, api_client):
        """F-F-04: lang=ru, описание на кириллице."""
        response = api_client.get_forecast(
            lat=55.75, lon=37.62, lang="ru", cnt=1
        )
        assert response.status_code == 200

        description = response.json()["list"][0]["weather"][0]["description"]
        assert re.search(r"[а-яА-ЯёЁ]", description), (
            f"Описание '{description}' не содержит кириллицу"
        )