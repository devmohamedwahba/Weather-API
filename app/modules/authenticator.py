import logging
from app.adapters.rest_client import RestClient
from app.core.config import config

logger = logging.getLogger(__name__)


class WeatherAuthenticator:
    def __init__(self, base_url, timeout=40):
        logger.info(f"Initiating {type(self).__name__} ...")
        self.base_url = base_url
        self.rest_client = RestClient(base_url=self.base_url, timeout=timeout)
        self.api_key = config.WEATHERSTACK_API_KEY
