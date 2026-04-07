"""This Module To Implement MCP Exception."""


class AppBaseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    @classmethod
    def get_subclass_name(cls):
        return cls.__name__

    def __str__(self):
        subclass_name = self.get_subclass_name()
        return f"{subclass_name} ===> {self.msg}"


class WrongStatusCodeException(AppBaseException):
    def __init__(self, msg="UNEXPECTED STATUS CODE"):
        self.msg = msg


class GenericException(AppBaseException):
    def __init__(self, msg="UNEXPECTED BEHAVIOR"):
        self.msg = msg


class ExternalAPIException(AppBaseException):
    def __init__(self, msg="EXTERNAL API ERROR", status_code=502, details=None):
        self.msg = msg
        self.status_code = status_code
        self.details = details or {}
