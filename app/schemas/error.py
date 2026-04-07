from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: int
    type: str
    info: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
