"""Async HTTP client built on httpx."""
import asyncio
import logging

import httpx

from app.core.exceptions import AppBaseException

logger = logging.getLogger(__name__)


class RestClientException(AppBaseException):
    status_code = 503

    def __init__(self, msg="External service is unavailable"):
        self.msg = msg


class RestClient:
    def __init__(
        self,
        base_url: str,
        authorization_header: str | None = None,
        timeout: int = 10,
        verify_ssl: bool = True,
        max_retry: int = 2,
        retry_wait: float = 3,
    ):
        logger.info(f"Initiating {type(self).__name__}")
        self.base_url = base_url
        self.authorization_header = authorization_header
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retry = max_retry
        self.retry_wait = retry_wait

    async def send(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
        accept: str = "application/json",
        expected_status: int | None = None,
        fail_request: bool = True,
        timeout: int | None = None,
    ) -> dict | bytes | None:
        """Send an HTTP request with retry logic.

        Parameters
        ----------
        endpoint : str
            Path appended to base_url.
        method : str
            HTTP method (GET, POST, …).
        params : dict | None
            Query parameters.
        data : dict | None
            JSON body payload.
        headers : dict | None
            Extra headers merged with defaults.
        accept : str
            Accept header value.
        expected_status : int | None
            Exact expected status code. If None, any 2xx is accepted.
        fail_request : bool
            Raise on failure after retries.
        timeout : int | None
            Per-request timeout override.
        """
        url = self.base_url + endpoint
        req_headers = self._build_headers(accept, headers)
        effective_timeout = timeout or self.timeout

        response = None
        for _ in range(self.max_retry):
            response = await self._do_request(
                method, url, params, data, req_headers, effective_timeout
            )
            if response is not None and self._validate_response(
                response.status_code, expected_status
            ):
                return self._parse_response(response, accept)

            await asyncio.sleep(self.retry_wait)

        if fail_request:
            self._fail_request(method, url, response)

    def _build_headers(self, accept: str, extra: dict | None = None) -> dict:
        h: dict[str, str] = {"Accept": accept}
        if self.authorization_header:
            h["Authorization"] = self.authorization_header
        if extra:
            h.update(extra)
        return h

    async def _do_request(
        self, method: str, url: str, params, data, headers, timeout
    ) -> httpx.Response | None:
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.request(
                    method, url, params=params, json=data, headers=headers, timeout=timeout
                )
                return response
        except Exception as ex:
            logger.error(f"Failed to {method} {url} | {ex}", exc_info=True)
            return None

    @staticmethod
    def _validate_response(status_code: int, expected_status: int | None) -> bool:
        if expected_status:
            return status_code == expected_status
        return 200 <= status_code < 300

    @staticmethod
    def _parse_response(response: httpx.Response, accept: str) -> dict | bytes:
        if not response.text:
            return {}
        content_type = response.headers.get("content-type", "")
        if "application/json" in accept or "application/json" in content_type:
            return response.json()
        return response.content

    @classmethod
    def _fail_request(cls, method: str, url: str, response: httpx.Response | None):
        if response is not None:
            logger.error(
                f"Failed HTTP request: {method} {url} with Status: {response.status_code}",
                exc_info=True,
            )
            logger.error(response.text, exc_info=True)
        else:
            logger.error(f"Failed HTTP request: {method} {url} — no response", exc_info=True)
        raise RestClientException()
