import base64
import secrets

from loguru import logger
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

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


class SwaggerBasicAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to protect Swagger UI and OpenAPI endpoints with Basic Auth."""

    PROTECTED_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request, call_next):
        if request.url.path not in self.PROTECTED_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return self._unauthorized_response()

        try:
            encoded_credentials = auth_header.split(" ", 1)[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            return self._unauthorized_response()

        is_valid_username = secrets.compare_digest(username, settings.swagger_username)
        is_valid_password = secrets.compare_digest(password, settings.swagger_password)

        if not (is_valid_username and is_valid_password):
            return self._unauthorized_response()

        return await call_next(request)

    @staticmethod
    def _unauthorized_response() -> Response:
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Unauthorized",
            headers={"WWW-Authenticate": "Basic realm='Swagger UI'"},
        )
