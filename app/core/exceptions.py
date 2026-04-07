"""This Module To Implement MCP Exception."""


class AppBaseException(Exception):
    status_code: int = 500
    error_code: int = 500
    error_type: str = "internal_error"

    def __init__(self, msg: str = "An unexpected error occurred"):
        self.msg = msg

    @classmethod
    def get_subclass_name(cls):
        return cls.__name__

    def __str__(self):
        subclass_name = self.get_subclass_name()
        return f"{subclass_name} ===> {self.msg}"


class UnauthorizedException(AppBaseException):
    status_code = 401
    error_code = 101
    error_type = "unauthorized"

    def __init__(self, msg="You have not supplied valid credentials."):
        self.msg = msg


class NotFoundException(AppBaseException):
    status_code = 404
    error_code = 404
    error_type = "not_found"

    def __init__(self, msg="The requested resource was not found."):
        self.msg = msg


class WrongStatusCodeException(AppBaseException):
    status_code = 502
    error_code = 502
    error_type = "bad_gateway"

    def __init__(self, msg="UNEXPECTED STATUS CODE"):
        self.msg = msg


class GenericException(AppBaseException):
    status_code = 500
    error_code = 500
    error_type = "internal_error"

    def __init__(self, msg="UNEXPECTED BEHAVIOR"):
        self.msg = msg


class ExternalAPIException(AppBaseException):
    status_code = 502
    error_code = 502
    error_type = "external_api_error"

    def __init__(self, msg="EXTERNAL API ERROR", details=None):
        self.msg = msg
        self.details = details
