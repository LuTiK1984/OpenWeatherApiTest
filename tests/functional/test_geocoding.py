import pytest

"""pytest tests/functional/test_geocoding.py -v"""
class TestGeocodingFunctional:
    """Функциональные тесты GET /geo/1.0/direct"""

    @pytest.mark.functional
    def test_basic_request(self, api_client):
        """G-F-01: Базовый запрос по названию города."""
        response = api_client.get_geocoding_direct(q="London")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "London"
        assert data[0]["country"] == "GB"

    @pytest.mark.functional
    def test_limit_one(self, api_client):
        """G-F-02: limit=1 — ровно один результат."""
        response = api_client.get_geocoding_direct(q="London", limit=1)
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.functional
    def test_limit_five(self, api_client):
        """G-F-03: limit=5 — несколько London в мире."""
        response = api_client.get_geocoding_direct(q="London", limit=5)
        assert response.status_code == 200

        data = response.json()
        assert 1 <= len(data) <= 5

    @pytest.mark.functional
    def test_city_with_country_code(self, api_client):
        """G-F-04: Город + страна (Paris,FR)."""
        response = api_client.get_geocoding_direct(q="Paris,FR")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert data[0]["country"] == "FR"

    @pytest.mark.functional
    def test_city_state_country_us(self, api_client):
        """G-F-05: Город + штат + страна (Springfield,IL,US)."""
        response = api_client.get_geocoding_direct(q="Springfield,IL,US")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert data[0]["country"] == "US"

    @pytest.mark.functional
    def test_cyrillic_query(self, api_client):
        """G-F-06: Кириллица (Москва)."""
        response = api_client.get_geocoding_direct(q="Москва")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert data[0]["country"] == "RU"

    @pytest.mark.functional
    def test_japanese_query(self, api_client):
        """G-F-07: Японский (東京)."""
        response = api_client.get_geocoding_direct(q="東京")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert data[0]["country"] == "JP"

    @pytest.mark.functional
    def test_local_names_field(self, api_client):
        """G-F-08: Поле local_names содержит переводы."""
        response = api_client.get_geocoding_direct(q="Moscow", limit=1)
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert "local_names" in data[0]
        assert "ru" in data[0]["local_names"]