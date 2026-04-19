import pytest

"""pytest tests/negative/test_error_handling.py -v"""
class TestCurrentWeatherNegative:
    """Негативные тесты GET /data/2.5/weather"""

    @pytest.mark.negative
    def test_missing_appid(self, api_client):
        """W-N-01: Запрос без API-ключа."""
        response = api_client.get_current_weather(
            lat=55.75, lon=37.62, appid=""
        )
        assert response.status_code == 401

    @pytest.mark.negative
    def test_invalid_appid(self, api_client):
        """W-N-02: Невалидный API-ключ."""
        response = api_client.get_current_weather(
            lat=55.75, lon=37.62, appid="INVALID_KEY_12345"
        )
        assert response.status_code == 401

    @pytest.mark.negative
    def test_missing_all_params(self, api_client):
        """W-N-03: Только appid, без координат и q."""
        response = api_client.get_current_weather()
        assert response.status_code == 400

    @pytest.mark.negative
    def test_missing_lon(self, api_client):
        """W-N-04: Только lat, без lon."""
        response = api_client.get_current_weather(lat=55.75)
        assert response.status_code == 400

    @pytest.mark.negative
    def test_missing_lat(self, api_client):
        """W-N-05: Только lon, без lat."""
        response = api_client.get_current_weather(lon=37.62)
        assert response.status_code == 400

    @pytest.mark.negative
    def test_nonexistent_city(self, api_client):
        """W-N-06: Несуществующий город."""
        response = api_client.get_current_weather(q="xyznonexistent123")
        assert response.status_code == 404

        data = response.json()
        assert data["message"] == "city not found"

    @pytest.mark.negative
    def test_invalid_units_ignored(self, api_client):
        """W-N-07: Невалидный units — API должен вернуть 200 (игнорирует)."""
        response = api_client.get_current_weather(
            lat=51.51, lon=-0.13, units="banana"
        )
        # Проверяем фактическое поведение: API игнорирует невалидный units
        assert response.status_code == 200

        # Температура должна быть в Кельвинах (standard по умолчанию)
        temp = response.json()["main"]["temp"]
        assert temp > 170, "При невалидном units ожидаются Кельвины (standard)"

    @pytest.mark.negative
    def test_invalid_lang_ignored(self, api_client):
        """W-N-08: Невалидный lang — API должен вернуть 200 (игнорирует)."""
        response = api_client.get_current_weather(
            lat=51.51, lon=-0.13, lang="zzz"
        )
        assert response.status_code == 200

        # При невалидном lang описание должно быть на английском
        description = response.json()["weather"][0]["description"]
        assert description.isascii(), (
            f"Ожидался английский, получено: '{description}'"
        )


class TestForecastNegative:
    """Негативные тесты GET /data/2.5/forecast"""

    @pytest.mark.negative
    def test_missing_appid(self, api_client):
        """F-N-01: Запрос без API-ключа."""
        response = api_client.get_forecast(
            lat=55.75, lon=37.62, appid=""
        )
        assert response.status_code == 401

    @pytest.mark.negative
    def test_invalid_appid(self, api_client):
        """F-N-02: Невалидный API-ключ."""
        response = api_client.get_forecast(
            lat=55.75, lon=37.62, appid="INVALID_KEY_12345"
        )
        assert response.status_code == 401

    @pytest.mark.negative
    def test_missing_all_params(self, api_client):
        """F-N-03: Без координат."""
        response = api_client.get_forecast()
        assert response.status_code == 400

    @pytest.mark.negative
    def test_cnt_zero(self, api_client):
        """F-N-04: cnt=0 — проверяем фактическое поведение."""
        response = api_client.get_forecast(
            lat=55.75, lon=37.62, cnt=0
        )
        assert response.status_code == 200

        data = response.json()
        # cnt=0 может вернуть пустой list или значение по умолчанию
        assert isinstance(data["list"], list)

    @pytest.mark.negative
    def test_cnt_negative(self, api_client):
        """F-N-05: cnt=-1 — проверяем фактическое поведение."""
        response = api_client.get_forecast(
            lat=55.75, lon=37.62, cnt=-1
        )
        # API может вернуть 200 с дефолтным значением или 400
        assert response.status_code in (200, 400)

class TestGeocodingNegative:
    """Негативные тесты GET /geo/1.0/direct"""

    @pytest.mark.negative
    def test_missing_appid(self, api_client):
        """G-N-01: Запрос без API-ключа."""
        response = api_client.get_geocoding_direct(q="London", appid="")
        assert response.status_code == 401

    @pytest.mark.negative
    def test_invalid_appid(self, api_client):
        """G-N-02: Невалидный API-ключ."""
        response = api_client.get_geocoding_direct(
            q="London", appid="INVALID_KEY_12345"
        )
        assert response.status_code == 401

    @pytest.mark.negative
    def test_missing_q(self, api_client):
        """G-N-03: Без параметра q."""
        response = api_client.get_geocoding_direct()
        assert response.status_code == 400

    @pytest.mark.negative
    def test_nonexistent_city(self, api_client):
        """G-N-04: Несуществующий город — пустой массив."""
        response = api_client.get_geocoding_direct(q="xyznonexistent123")
        assert response.status_code == 200

        data = response.json()
        assert data == [], f"Ожидался пустой массив, получено: {data}"

    @pytest.mark.negative
    def test_empty_q(self, api_client):
        """G-N-05: Пустой q."""
        response = api_client.get_geocoding_direct(q="")
        assert response.status_code == 400