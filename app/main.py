from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.middlewares import (
    RateLimitMiddleware,
    ExceptionMiddleware,
    SwaggerBasicAuthMiddleware,
    RequestIDMiddleware,
)
from app.api.v1 import router as v1_router
from app.utils import startup_application, shutdown_application


@asynccontextmanager
async def lifespan(app_local: FastAPI):
    await startup_application(app_local)

    yield

    await shutdown_application(app_local)

    logger.info("Shutdown application...")


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allowed_credentials,
    allow_methods=settings.cors_allowed_methods,
    allow_headers=settings.cors_allowed_headers,
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(SwaggerBasicAuthMiddleware)


# Include API routers
app.include_router(v1_router, prefix="/api")
