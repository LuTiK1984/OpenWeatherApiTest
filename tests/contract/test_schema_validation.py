import pytest
from pydantic import ValidationError
from api_client.models import (
    CurrentWeatherResponse,
    ForecastResponse,
    GeocodingItem,
)

"""pytest tests/contract/test_schema_validation.py -v"""
class TestCurrentWeatherContract:
    """Контрактные тесты GET /data/2.5/weather"""

    @pytest.fixture()
    def weather_data(self, api_client):
        """Один запрос, переиспользуется в нескольких проверках."""
        response = api_client.get_current_weather(
            lat=55.75, lon=37.62, units="metric"
        )
        assert response.status_code == 200
        return response.json()

    @pytest.mark.contract
    def test_full_schema_validation(self, weather_data):
        """W-C-01..10: Полная валидация через pydantic-модель."""
        try:
            CurrentWeatherResponse(**weather_data)
        except ValidationError as e:
            pytest.fail(f"Ответ не соответствует схеме:\n{e}")

    @pytest.mark.contract
    def test_coord_types(self, weather_data):
        """W-C-01: coord содержит lat (float) и lon (float)."""
        coord = weather_data["coord"]
        assert isinstance(coord["lat"], (int, float))
        assert isinstance(coord["lon"], (int, float))

    @pytest.mark.contract
    def test_weather_array_structure(self, weather_data):
        """W-C-02: weather — непустой массив с правильной структурой."""
        weather = weather_data["weather"]
        assert isinstance(weather, list)
        assert len(weather) >= 1

        for item in weather:
            assert isinstance(item["id"], int)
            assert isinstance(item["main"], str)
            assert isinstance(item["description"], str)
            assert isinstance(item["icon"], str)

    @pytest.mark.contract
    def test_main_fields_are_numbers(self, weather_data):
        """W-C-03: main.temp, feels_like, pressure, humidity — числа."""
        main = weather_data["main"]
        assert isinstance(main["temp"], (int, float))
        assert isinstance(main["feels_like"], (int, float))
        assert isinstance(main["pressure"], (int, float))
        assert isinstance(main["humidity"], (int, float))

    @pytest.mark.contract
    def test_humidity_range(self, weather_data):
        """W-C-04: humidity в диапазоне 0–100."""
        humidity = weather_data["main"]["humidity"]
        assert 0 <= humidity <= 100

    @pytest.mark.contract
    def test_wind_values(self, weather_data):
        """W-C-05: wind.speed >= 0, wind.deg в 0–360."""
        wind = weather_data["wind"]
        assert wind["speed"] >= 0
        assert 0 <= wind["deg"] <= 360

    @pytest.mark.contract
    def test_visibility_range(self, weather_data):
        """W-C-06: visibility в диапазоне 0–10000."""
        assert 0 <= weather_data["visibility"] <= 10000

    @pytest.mark.contract
    def test_dt_positive_timestamp(self, weather_data):
        """W-C-07: dt — положительное целое число."""
        dt = weather_data["dt"]
        assert isinstance(dt, int)
        assert dt > 0

    @pytest.mark.contract
    def test_sunrise_before_sunset(self, weather_data):
        """W-C-08: sys.sunrise < sys.sunset."""
        sys = weather_data["sys"]
        assert sys["sunrise"] < sys["sunset"]

    @pytest.mark.contract
    def test_cod_is_integer_200(self, weather_data):
        """W-C-09: cod = 200 (число, не строка)."""
        assert weather_data["cod"] == 200
        assert isinstance(weather_data["cod"], int)

    @pytest.mark.contract
    def test_timezone_is_integer(self, weather_data):
        """W-C-10: timezone — целое число."""
        assert isinstance(weather_data["timezone"], int)


class TestForecastContract:
    """Контрактные тесты GET /data/2.5/forecast"""

    @pytest.fixture()
    def forecast_data(self, api_client):
        response = api_client.get_forecast(lat=55.75, lon=37.62)
        assert response.status_code == 200
        return response.json()

    @pytest.mark.contract
    def test_full_schema_validation(self, forecast_data):
        """F-C-01..09: Полная валидация через pydantic-модель."""
        try:
            ForecastResponse(**forecast_data)
        except ValidationError as e:
            pytest.fail(f"Ответ не соответствует схеме:\n{e}")

    @pytest.mark.contract
    def test_cod_is_string(self, forecast_data):
        """F-C-01: cod = '200' (строка, не число)."""
        assert forecast_data["cod"] == "200"
        assert isinstance(forecast_data["cod"], str)

    @pytest.mark.contract
    def test_cnt_matches_list_length(self, forecast_data):
        """F-C-02: cnt совпадает с длиной list."""
        assert forecast_data["cnt"] == len(forecast_data["list"])

    @pytest.mark.contract
    def test_list_item_structure(self, forecast_data):
        """F-C-03: Каждый элемент list содержит обязательные поля."""
        required_keys = {"dt", "main", "weather", "wind", "clouds", "pop", "dt_txt"}
        for item in forecast_data["list"]:
            missing = required_keys - set(item.keys())
            assert not missing, f"Отсутствуют поля: {missing}"

    @pytest.mark.contract
    def test_pop_range(self, forecast_data):
        """F-C-04: pop в диапазоне 0.0–1.0."""
        for item in forecast_data["list"]:
            assert 0.0 <= item["pop"] <= 1.0, (
                f"pop={item['pop']} вне диапазона в dt={item['dt']}"
            )

    @pytest.mark.contract
    def test_dt_ascending_order(self, forecast_data):
        """F-C-05: dt в list идут по возрастанию."""
        timestamps = [item["dt"] for item in forecast_data["list"]]
        assert timestamps == sorted(timestamps)

    @pytest.mark.contract
    def test_dt_step_three_hours(self, forecast_data):
        """F-C-06: Шаг между dt = 10800 сек (3 часа)."""
        timestamps = [item["dt"] for item in forecast_data["list"]]
        for i in range(1, len(timestamps)):
            step = timestamps[i] - timestamps[i - 1]
            assert step == 10800, (
                f"Шаг между [{i-1}] и [{i}] = {step}, ожидалось 10800"
            )

    @pytest.mark.contract
    def test_city_structure(self, forecast_data):
        """F-C-07: city содержит обязательные поля."""
        city = forecast_data["city"]
        for key in ("id", "name", "country", "coord", "timezone"):
            assert key in city, f"Отсутствует city.{key}"

    @pytest.mark.contract
    def test_sys_pod_values(self, forecast_data):
        """F-C-08: sys.pod — 'd' или 'n'."""
        for item in forecast_data["list"]:
            pod = item["sys"]["pod"]
            assert pod in ("d", "n"), f"sys.pod='{pod}', ожидалось 'd' или 'n'"

    @pytest.mark.contract
    def test_rain_key_is_3h(self, forecast_data):
        """F-C-09: Если дождь — ключ rain.3h, а не rain.1h."""
        for item in forecast_data["list"]:
            if "rain" in item:
                assert "3h" in item["rain"], (
                    f"В forecast ожидается rain.3h, найдено: {item['rain'].keys()}"
                )
                assert "1h" not in item["rain"]


class TestGeocodingContract:
    """Контрактные тесты GET /geo/1.0/direct"""

    @pytest.fixture()
    def geocoding_data(self, api_client):
        response = api_client.get_geocoding_direct(q="Moscow", limit=5)
        assert response.status_code == 200
        return response.json()

    @pytest.mark.contract
    def test_response_is_list(self, geocoding_data):
        """G-C-01: Ответ — массив."""
        assert isinstance(geocoding_data, list)

    @pytest.mark.contract
    def test_item_structure_and_types(self, geocoding_data):
        """G-C-02: Каждый элемент содержит name, lat, lon, country."""
        for item in geocoding_data:
            try:
                GeocodingItem(**item)
            except Exception as e:
                pytest.fail(f"Элемент не прошёл валидацию: {e}\nДанные: {item}")

    @pytest.mark.contract
    def test_coordinates_range(self, geocoding_data):
        """G-C-03: lat в [-90, 90], lon в [-180, 180]."""
        for item in geocoding_data:
            assert -90 <= item["lat"] <= 90
            assert -180 <= item["lon"] <= 180

    @pytest.mark.contract
    def test_country_code_format(self, geocoding_data):
        """G-C-04: country — строка из 2 символов (ISO 3166)."""
        for item in geocoding_data:
            assert len(item["country"]) == 2
            assert item["country"].isalpha()

    @pytest.mark.contract
    def test_results_within_limit(self, api_client):
        """G-C-05: Длина массива <= limit."""
        response = api_client.get_geocoding_direct(q="London", limit=3)
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 3