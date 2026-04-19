from pydantic import BaseModel, Field
from typing import Optional


class Coord(BaseModel):
    lon: float
    lat: float


class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class MainWeather(BaseModel):
    temp: float
    feels_like: float
    pressure: int
    humidity: int = Field(ge=0, le=100)
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    sea_level: Optional[int] = None
    grnd_level: Optional[int] = None


class Wind(BaseModel):
    speed: float = Field(ge=0)
    deg: int = Field(ge=0, le=360)
    gust: Optional[float] = None


class Clouds(BaseModel):
    all: int = Field(ge=0, le=100)


class Sys(BaseModel):
    type: Optional[int] = None
    id: Optional[int] = None
    country: str
    sunrise: int
    sunset: int


class CurrentWeatherResponse(BaseModel):
    """Модель ответа GET /data/2.5/weather"""
    coord: Coord
    weather: list[WeatherCondition] = Field(min_length=1)
    base: str
    main: MainWeather
    visibility: int = Field(ge=0, le=10000)
    wind: Wind
    clouds: Clouds
    dt: int = Field(gt=0)
    sys: Sys
    timezone: int
    id: int
    name: str
    cod: int


class ForecastItem(BaseModel):
    """Один элемент прогноза в list[]"""
    dt: int = Field(gt=0)
    main: MainWeather
    weather: list[WeatherCondition] = Field(min_length=1)
    clouds: Clouds
    wind: Wind
    visibility: int = Field(ge=0)
    pop: float = Field(ge=0, le=1)
    dt_txt: str


class ForecastCity(BaseModel):
    id: int
    name: str
    coord: Coord
    country: str
    timezone: int
    sunrise: int
    sunset: int
    population: Optional[int] = None


class ForecastResponse(BaseModel):
    """Модель ответа GET /data/2.5/forecast"""
    cod: str  # "200" — строка, не число!
    message: float | int
    cnt: int
    list: list[ForecastItem]
    city: ForecastCity


class GeocodingItem(BaseModel):
    """Один элемент ответа GET /geo/1.0/direct"""
    name: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    country: str = Field(min_length=2, max_length=2)
    state: Optional[str] = None
    local_names: Optional[dict] = None