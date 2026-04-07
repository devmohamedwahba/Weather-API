from fastapi import APIRouter
from app.modules.client import WeatherClient

router = APIRouter()


@router.get("/current", summary="Current Weather")
async def current_weather():
    client = WeatherClient()
    data = client.get_weather_instance().get_current_weather("London")
    return {"message": "Success", "data": data}
