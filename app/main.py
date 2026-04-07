import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import config

from app.api.routes import health
from app.api.routes import weather
from app.core.exceptions import AppBaseException
from app.schemas.error import ErrorResponse, ErrorDetail
from app.core.logging_conf import configure_logging
from asgi_correlation_id import CorrelationIdMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()


app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description=config.DESCRIPTION,
    openapi_url=f"{config.API_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(health.router, prefix=config.API_PREFIX, tags=["health"])
app.include_router(weather.router, prefix=config.API_PREFIX, tags=["weather"])


def _error_response(status_code: int, code: int, error_type: str, info: str) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, type=error_type, info=info))
    return JSONResponse(status_code=status_code, content=body.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return _error_response(exc.status_code, exc.status_code, "http_error", str(exc.detail))


@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    logger.error(str(exc))
    return _error_response(exc.status_code, exc.error_code, exc.error_type, exc.msg)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return _error_response(500, 500, "internal_error", "Internal server error")
