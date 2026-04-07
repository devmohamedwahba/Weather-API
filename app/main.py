import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import config
from app.core.exceptions import ExternalAPIException
from app.api.routes import health
from app.api.routes import weather
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


@app.exception_handler(ExternalAPIException)
async def handle_external_api_exception(request: Request, exc: ExternalAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.details or {"message": exc.msg},
        },
    )
