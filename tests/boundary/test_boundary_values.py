import pytest

"""pytest tests/boundary/test_boundary_values.py -v"""
class TestCurrentWeatherBoundary:
    """Граничные тесты GET /data/2.5/weather"""

    @pytest.mark.boundary
    def test_north_pole(self, api_client):
        """W-B-01: Северный полюс."""
        response = api_client.get_current_weather(lat=90, lon=0)
        assert response.status_code == 200
        assert "main" in response.json()

    @pytest.mark.boundary
    def test_south_pole(self, api_client):
        """W-B-02: Южный полюс."""
        response = api_client.get_current_weather(lat=-90, lon=0)
        assert response.status_code == 200
        assert "main" in response.json()

    @pytest.mark.boundary
    def test_max_longitude(self, api_client):
        """W-B-03: Крайний восток (lon=180)."""
        response = api_client.get_current_weather(lat=0, lon=180)
        assert response.status_code == 200
        assert "main" in response.json()

    @pytest.mark.boundary
    def test_min_longitude(self, api_client):
        """W-B-04: Крайний запад (lon=-180)."""
        response = api_client.get_current_weather(lat=0, lon=-180)
        assert response.status_code == 200
        assert "main" in response.json()

    @pytest.mark.boundary
    def test_lat_above_max(self, api_client):
        """W-B-05: lat=91 — за границей допустимого."""
        response = api_client.get_current_weather(lat=91, lon=0)
        # API может вернуть 400 или округлить до 90
        if response.status_code == 200:
            lat = response.json()["coord"]["lat"]
            assert -90 <= lat <= 90, f"lat={lat} вне допустимого диапазона"
        else:
            assert response.status_code == 400

    @pytest.mark.boundary
    def test_lat_below_min(self, api_client):
        """W-B-06: lat=-91 — за границей допустимого."""
        response = api_client.get_current_weather(lat=-91, lon=0)
        if response.status_code == 200:
            lat = response.json()["coord"]["lat"]
            assert -90 <= lat <= 90
        else:
            assert response.status_code == 400

    @pytest.mark.boundary
    def test_lon_above_max(self, api_client):
        """W-B-07: lon=181 — за границей допустимого."""
        response = api_client.get_current_weather(lat=0, lon=181)
        if response.status_code == 200:
            lon = response.json()["coord"]["lon"]
            assert -180 <= lon <= 180, f"lon={lon} вне допустимого диапазона"
        else:
            assert response.status_code == 400

    @pytest.mark.boundary
    def test_zero_coordinates(self, api_client):
        """W-B-08: Нулевые координаты (Гвинейский залив)."""
        response = api_client.get_current_weather(lat=0, lon=0)
        assert response.status_code == 200
        assert "main" in response.json()

    @pytest.mark.boundary
    def test_fractional_coordinates(self, api_client):
        """W-B-09: Дробные координаты (Париж)."""
        response = api_client.get_current_weather(lat=48.8566, lon=2.3522)
        assert response.status_code == 200
        assert "main" in response.json()

    @pytest.mark.boundary
    def test_deprecated_q_empty_string(self, api_client):
        """W-B-10: q — пустая строка."""
        response = api_client.get_current_weather(q="")
        assert response.status_code in (400, 404)

    @pytest.mark.boundary
    def test_deprecated_q_very_long_string(self, api_client):
        """W-B-11: q — строка 10000 символов."""
        long_name = "a" * 10000
        response = api_client.get_current_weather(q=long_name)
        # Главное — не 500 (Internal Server Error)
        assert response.status_code != 500
        assert response.status_code in (400, 404, 414)

    @pytest.mark.boundary
    def test_deprecated_q_unicode_cyrillic(self, api_client):
        """W-B-12: q с кириллицей."""
        response = api_client.get_current_weather(q="Москва")
        assert response.status_code == 200

        data = response.json()
        assert data["sys"]["country"] == "RU"

    @pytest.mark.boundary
    def test_deprecated_q_special_characters(self, api_client):
        """W-B-13: q со спецсимволами — не должен вызвать 500."""
        response = api_client.get_current_weather(q="<script>alert(1)</script>")
        assert response.status_code != 500
        assert response.status_code in (400, 404)


class TestGeocodingBoundary:
    """Граничные тесты GET /geo/1.0/direct"""

    @pytest.mark.boundary
    def test_limit_zero(self, api_client):
        """G-B-01: limit=0."""
        response = api_client.get_geocoding_direct(q="London", limit=0)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.boundary
    def test_limit_above_max(self, api_client):
        """G-B-02: limit=100 — больше максимума (5)."""
        response = api_client.get_geocoding_direct(q="London", limit=100)
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 5, f"Вернулось {len(data)} результатов, макс. по доке — 5"

    @pytest.mark.boundary
    def test_very_long_query(self, api_client):
        """G-B-03: Очень длинная строка q."""
        long_name = "a" * 10000
        response = api_client.get_geocoding_direct(q=long_name)
        assert response.status_code != 500

    @pytest.mark.boundary
    def test_special_characters(self, api_client):
        """G-B-04: Спецсимволы в q."""
        response = api_client.get_geocoding_direct(q="<>&\"'")
        assert response.status_code != 500

    @pytest.mark.boundary
    def test_single_character(self, api_client):
        """G-B-05: Один символ в q."""
        response = api_client.get_geocoding_direct(q="A")
        assert response.status_code == 200
        assert isinstance(response.json(), list)