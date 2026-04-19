import pytest
from api_client.client import WeatherApiClient


@pytest.fixture(scope="session")
def api_client():
    """Клиент API, переиспользуется во всех тестах."""
    return WeatherApiClient()