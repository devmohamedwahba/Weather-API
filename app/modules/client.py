import logging
from app.core.config import config
from app.modules.authenticator import WeatherAuthenticator
from app.modules.weather import Weather

logger = logging.getLogger(__name__)


class WeatherClient:
    def __init__(self):
        logger.info(f"Initiating {type(self).__name__} ...")
        self.base_url = config.WEATHERSTACK_API_BASE_URL
        self.authenticator = WeatherAuthenticator(base_url=self.base_url.strip("/"), timeout=40)

    def get_weather_instance(self):
        return Weather(authenticator=self.authenticator)
