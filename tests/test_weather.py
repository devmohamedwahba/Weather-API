import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

SAMPLE_WEATHER_DATA = {
    "request": {
        "type": "City",
        "query": "London, United Kingdom",
        "language": "en",
        "unit": "m",
    },
    "location": {
        "name": "London",
        "country": "United Kingdom",
        "region": "City of London, Greater London",
        "lat": "51.517",
        "lon": "-0.106",
        "timezone_id": "Europe/London",
        "localtime": "2026-04-07 12:00",
        "localtime_epoch": 1775649600,
        "utc_offset": "1.0",
    },
    "current": {
        "observation_time": "11:00 AM",
        "temperature": 15,
        "weather_code": 116,
        "weather_icons": ["https://example.com/icon.png"],
        "weather_descriptions": ["Partly cloudy"],
        "astro": {
            "sunrise": "06:30 AM",
            "sunset": "07:45 PM",
            "moonrise": "03:15 PM",
            "moonset": "04:30 AM",
            "moon_phase": "Waxing Gibbous",
            "moon_illumination": 75,
        },
        "air_quality": {
            "co": "230.5",
            "no2": "12.3",
            "o3": "45.6",
            "so2": "5.2",
            "pm2_5": "8.1",
            "pm10": "15.4",
            "us-epa-index": "1",
            "gb-defra-index": "2",
        },
        "wind_speed": 13,
        "wind_degree": 210,
        "wind_dir": "SSW",
        "pressure": 1012,
        "precip": 0.0,
        "humidity": 72,
        "cloudcover": 50,
        "feelslike": 14,
        "uv_index": 4,
        "visibility": 10,
        "is_day": "yes",
    },
}


@pytest.mark.asyncio
async def test_current_weather_cache_miss(client: AsyncClient):
    """When cache misses, should call the external API and return fresh data."""
    mock_weather = MagicMock()
    mock_weather.get_current_weather = AsyncMock(return_value=SAMPLE_WEATHER_DATA)

    mock_client_instance = MagicMock()
    mock_client_instance.get_weather_instance.return_value = mock_weather

    with (
        patch("app.api.routes.weather.cache") as mock_cache,
        patch("app.api.routes.weather.WeatherClient", return_value=mock_client_instance),
    ):
        mock_cache.get.return_value = None

        response = await client.get("/api/v1/current", params={"query": "London"})

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Success"
        assert body["data"]["location"]["name"] == "London"
        assert body["data"]["current"]["temperature"] == 15

        mock_cache.get.assert_called_once_with("weather:current:london")
        mock_weather.get_current_weather.assert_called_once_with("London")
        mock_cache.set.assert_called_once_with("weather:current:london", SAMPLE_WEATHER_DATA)


@pytest.mark.asyncio
async def test_current_weather_cache_hit(client: AsyncClient):
    """When cache hits, should return cached data without calling the API."""
    with (
        patch("app.api.routes.weather.cache") as mock_cache,
        patch("app.api.routes.weather.WeatherClient") as mock_client_cls,
    ):
        mock_cache.get.return_value = SAMPLE_WEATHER_DATA

        response = await client.get("/api/v1/current", params={"query": "London"})

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Success (cached)"
        assert body["data"]["location"]["name"] == "London"

        mock_client_cls.assert_not_called()
        mock_cache.set.assert_not_called()


@pytest.mark.asyncio
async def test_current_weather_query_stripped_and_lowered(client: AsyncClient):
    """Cache key should be normalized (lowercase + stripped)."""
    with (
        patch("app.api.routes.weather.cache") as mock_cache,
        patch("app.api.routes.weather.WeatherClient"),
    ):
        mock_cache.get.return_value = SAMPLE_WEATHER_DATA

        await client.get("/api/v1/current", params={"query": "  LONDON  "})

        mock_cache.get.assert_called_once_with("weather:current:london")


@pytest.mark.asyncio
async def test_current_weather_missing_query(client: AsyncClient):
    """Should return 422 when query param is missing."""
    response = await client.get("/api/v1/current")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_current_weather_api_exception(client: AsyncClient):
    """When the external API raises, the exception handler should catch it."""
    from app.core.exceptions import WrongStatusCodeException

    mock_weather = MagicMock()
    mock_weather.get_current_weather = AsyncMock(
        side_effect=WrongStatusCodeException()
    )

    mock_client_instance = MagicMock()
    mock_client_instance.get_weather_instance.return_value = mock_weather

    with (
        patch("app.api.routes.weather.cache") as mock_cache,
        patch("app.api.routes.weather.WeatherClient", return_value=mock_client_instance),
    ):
        mock_cache.get.return_value = None

        response = await client.get("/api/v1/current", params={"query": "Unknown"})

        assert response.status_code == 502
        body = response.json()
        assert body["success"] is False
        assert body["error"]["type"] == "bad_gateway"


@pytest.mark.asyncio
async def test_current_weather_generic_exception():
    """Unhandled exceptions should return 500."""
    from app.main import app as _app

    mock_client_instance = MagicMock()
    mock_client_instance.get_weather_instance.side_effect = RuntimeError("boom")

    with (
        patch("app.api.routes.weather.cache") as mock_cache,
        patch("app.api.routes.weather.WeatherClient", return_value=mock_client_instance),
    ):
        mock_cache.get.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as ac:
            response = await ac.get("/api/v1/current", params={"query": "London"})

        assert response.status_code == 500
        body = response.json()
        assert body["success"] is False
        assert body["error"]["type"] == "internal_error"
