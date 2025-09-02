import sys
from functools import wraps

from fastapi import FastAPI
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, Base
from app.factories import cache_factory


def rate_limit(
    max_requests: int = settings.rate_limit_requests,
    time_window: int = settings.rate_limit_time_window,
):
    """Decorator to apply rate limiting to FastAPI route handlers."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache from kwargs (assuming it's passed in the request context)
            request = kwargs.get("request")

            if request is None:
                raise ValueError("Request object must be passed to the route handler.")

            client_ip = request.client.host
            route_name = request.url.path
            cache = request.app.state.cache

            # Key for storing request count
            key = f"rate_limit:{client_ip}:{route_name}"

            request_count = await cache.get(key)

            if request_count is None:
                await cache.set(key, 1, ttl=time_window)

            elif int(request_count) >= max_requests:
                # Too many requests
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too many requests. Try again later."},
                )
            else:
                await cache.increment(key)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def startup_application(app_local: FastAPI) -> None:
    """Initialize the Redis cache and database engine/session maker."""

    # Configure loguru logger
    LOG_LEVEL = "DEBUG" if settings.app_debug else "INFO"
    logger.add(sys.stdout, level=LOG_LEVEL)
    logger.add(
        "logs/app.log", level=LOG_LEVEL, rotation="10 MB", retention="7 days", compression="zip"
    )

    # Initialize Redis cache
    if not hasattr(app_local.state, "cache"):
        logger.info("🔧 Setting up Redis cache...")

        cache = await cache_factory()
        app_local.state.cache = cache

    logger.info("✅ Redis cache initialized.")

    # Initialize database engine and create tables
    if not hasattr(app_local.state, "db_engine"):
        logger.info("🔧 Setting up database engine...")
        app_local.state.db_engine = engine

    async with app_local.state.db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Database initialized and tables created.")


async def shutdown_application(app_local: FastAPI) -> None:
    """Dispose of the database engine and session maker."""

    await app_local.state.cache.close()
    logger.info("🧹 Redis cache closed.")
