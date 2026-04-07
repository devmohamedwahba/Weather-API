import logging

from fastapi import APIRouter, Query
from app.modules.client import WeatherClient
from app.schemas.weather import CurrentWeatherResponse
from app.core.cache import cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/current", summary="Current Weather", response_model=CurrentWeatherResponse)
async def current_weather(query: str = Query(..., description="City name or location")):
    cache_key = f"weather:current:{query.lower().strip()}"

    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Cache hit for query='{query}' key='{cache_key}'")
        return {"message": "Success (cached)", "data": cached}

    logger.info(f"Cache miss for query='{query}', fetching from API")
    client = WeatherClient()
    data = client.get_weather_instance().get_current_weather(query)

    cache.set(cache_key, data)
    logger.info(f"Cached response for query='{query}' key='{cache_key}'")
    return {"message": "Success", "data": data}
