"""This module implements the RestClient class to be used as a standard way of communication to another entity."""
import logging
import requests
import urllib3
import time
from app.core.exceptions import AppBaseException

logger = logging.getLogger(__name__)


class RestClientException(AppBaseException):
    def __init__(self, msg="Failed to send request"):
        self.msg = msg


class RestClient:
    def __init__(self, base_url, authorization_header=None, timeout=10, verify_ssl=False, ciphers_ssl=False,
                 max_retry=2, retry_wait=3):
        logger.info(f"Initiating {type(self).__name__}")
        self.base_url = base_url
        self.authorization_header = authorization_header
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.ciphers_ssl = ciphers_ssl
        self.max_retry = max_retry
        self.retry_wait = retry_wait

        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if self.ciphers_ssl:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

    def send(
            self,
            endpoint,
            method="GET",
            params=None,
            data=None,
            content_type=None,
            headers=None,
            auth=None,
            files=None,
            accept="application/json",
            expected_status=None,
            fail_request=True,
            timeout=None,
            overwrite_timeout=False
    ):

        """
        Parameters
        ----------
        endpoint: str - endpoint to send to ( will be concatenated with base_url )
        method: str - method of the request
        data: json/blob - data to be sent
        content_type: str - content type of the request data
        accept: str - content type of the response
        headers: dict - key value pairs of request header other than defaults
        auth: HttpBasicAuth
        params: dict - key value pairs of request parameters
        files: file objects - files to be sent in the request
        fail_request: bool - log response in case of failure
        timeout: int - timeout of the request
        overwrite_timeout: bool - if true will overwrite default timeout
        expected_status: str - exact expected status ( if not provided, response status will be verified in range 2xx )
        Returns
        -------
        """

        request_url = self.base_url + endpoint

        request = self._prepare_request(
            method=method,
            url=request_url,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
            files=files,
            content_type=content_type,
            accept=accept,
        )

        response = None
        for _ in range(self.max_retry):
            response = self._send_request(request=request, timeout=timeout, overwrite_timeout=overwrite_timeout)
            if response is not None and self._validate_response(
                    status_code=response.status_code, expected_status=expected_status
            ):
                return self._get_response(response=response, accept=accept)

            time.sleep(self.retry_wait)

        if fail_request:
            self._fail_request(request, response)

    def _prepare_request(self, method, url, data, params, headers, auth, files, content_type, accept):

        _headers = {}
        if content_type:
            _headers.update({"Content-Type": content_type})

        if accept:
            _headers.update({"Accept": accept})

        if self.authorization_header:
            _headers.update({"Authorization": self.authorization_header})

        if headers:
            _headers.update(headers)

        if isinstance(data, dict):
            request = requests.Request(method, url, json=data, params=params, headers=_headers, auth=auth,
                                       files=files).prepare()
        else:
            request = requests.Request(method, url, data=data, params=params, headers=_headers, auth=auth,
                                       files=files).prepare()

        return request

    def _send_request(self, request, timeout=None, overwrite_timeout=False):
        session = requests.session()
        try:
            if overwrite_timeout:
                timeout = timeout
            else:
                timeout = self.timeout
            response = session.send(request, timeout=timeout, verify=self.verify_ssl)
        except Exception as ex:
            logger.error(f"Failed to {request.method} {request.url} | {ex}", exc_info=True)
        else:
            return response
        finally:
            session.close()

    @classmethod
    def _validate_response(cls, status_code, expected_status):
        if expected_status:
            return status_code == expected_status
        else:
            return 200 <= status_code < 300

    @classmethod
    def _get_response(cls, response, accept):
        if response.text and len(response.text) > 0:
            if "multipart/form-data" in response.headers.get("Content-Type",
                                                             "") or "attachment" in response.headers.get(
                "Content-Disposition", ""):
                return response.content
            if (accept in ["application/json", "application/yang-data+json"] or response.headers.get("Content-Type") in
                    ["application/json", "application/yang-data+json"]):
                return response.json()
            else:
                return response.content
        else:
            return {}

    @classmethod
    def _fail_request(cls, request, response):
        logger.error(
            f"Failed HTTP request: {request.method} {request.url}" + f" with Status: {response.status_code}\n"
            if response is not None
            else "",
            exc_info=True,
        )
        if response is not None:
            logger.error(response.text + "\n", exc_info=True)
        raise RestClientException
