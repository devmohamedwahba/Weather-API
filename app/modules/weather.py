import logging

from app.core.exceptions import ExternalAPIException, WrongStatusCodeException

logger = logging.getLogger(__name__)



ENDPOINTS = {
    "CURRENT_WEATHER": "/current",
}


class Weather:
    def __init__(self, authenticator):
        logger.info(f"Initiating {type(self).__name__} ...")
        self.authenticator = authenticator

    async def get_current_weather(self, destination):
        data = await self._query_current_weather(destination)
        return data

    async def _query_current_weather(self, destination):
        params = {
            "query": destination,
            "access_key": self.authenticator.api_key,
        }
        response = await self.authenticator.rest_client.send(
            endpoint=f"{ENDPOINTS['CURRENT_WEATHER']}",
            method="GET",
            params=params,
            expected_status=200,
        )

        if response is None:
            raise WrongStatusCodeException()
        if isinstance(response, dict) and response.get("success") is False:
            provider_error = response.get("error", {})
            raise ExternalAPIException(
                msg="Weather provider returned an error",
                details=provider_error,
            )
        return response
