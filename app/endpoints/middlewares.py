from loguru import logger
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit the number of requests from a single IP address."""

    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        cache = request.app.state.cache
        key = f"rate_limit:{client_ip}"

        request_count = await cache.get(key)

        if request_count is None:
            logger.debug(f"rate limit request count: {request_count}")
            await cache.set(key, 1, ttl=settings.rate_limit_time_window)

        elif int(request_count) >= settings.rate_limit_requests:
            logger.info(f"{request_count} requests remaining.")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Try again later."},
            )

        else:
            await cache.increment(key)

        response = await call_next(request)

        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle unhandled exceptions and return a JSON response."""

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception(f"Unhandled exception: {e}")

            detail = str(e) if settings.app_debug else "Internal server error."

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": detail},
            )
