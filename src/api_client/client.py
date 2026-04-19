import requests
from api_client.config import API_KEY, BASE_URL


class WeatherApiClient:
    """Клиент для работы с OpenWeatherMap API."""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL

    def get_current_weather(self, **params) -> requests.Response:
        """GET /data/2.5/weather"""
        params.setdefault("appid", self.api_key)
        return requests.get(
            f"{self.base_url}/data/2.5/weather",
            params=params
        )

    def get_forecast(self, **params) -> requests.Response:
        """GET /data/2.5/forecast"""
        params.setdefault("appid", self.api_key)
        return requests.get(
            f"{self.base_url}/data/2.5/forecast",
            params=params
        )

    def get_geocoding_direct(self, **params) -> requests.Response:
        """GET /geo/1.0/direct"""
        params.setdefault("appid", self.api_key)
        return requests.get(
            f"{self.base_url}/geo/1.0/direct",
            params=params
        )