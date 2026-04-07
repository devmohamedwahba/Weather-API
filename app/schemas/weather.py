from pydantic import BaseModel, Field


class RequestInfo(BaseModel):
    type: str
    query: str
    language: str
    unit: str


class Location(BaseModel):
    name: str
    country: str
    region: str
    lat: str
    lon: str
    timezone_id: str
    localtime: str
    localtime_epoch: int
    utc_offset: str


class Astro(BaseModel):
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: int


class AirQuality(BaseModel):
    model_config = {"populate_by_name": True}

    co: str
    no2: str
    o3: str
    so2: str
    pm2_5: str
    pm10: str
    us_epa_index: str | None = Field(None, alias="us-epa-index")
    gb_defra_index: str | None = Field(None, alias="gb-defra-index")


class CurrentWeather(BaseModel):
    observation_time: str
    temperature: int
    weather_code: int
    weather_icons: list[str]
    weather_descriptions: list[str]
    astro: Astro
    air_quality: AirQuality
    wind_speed: int
    wind_degree: int
    wind_dir: str
    pressure: int
    precip: float
    humidity: int
    cloudcover: int
    feelslike: int
    uv_index: int
    visibility: int
    is_day: str


class WeatherData(BaseModel):
    request: RequestInfo
    location: Location
    current: CurrentWeather


class CurrentWeatherResponse(BaseModel):
    message: str
    data: WeatherData
