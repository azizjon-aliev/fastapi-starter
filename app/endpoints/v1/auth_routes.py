from fastapi import APIRouter, Depends
from fastapi import status
from starlette.responses import JSONResponse

from app.endpoints.dependencies import get_auth_service
from app.schemas.auth_schema import (
    RegisterRequestSchema,
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    LoginResponseSchema,
    RegisterResponseSchema,
    RefreshTokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login_endpoint(
    data: LoginRequestSchema, auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponseSchema:
    response = await auth_service.login(data=data)

    if response is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid credentials"}
        )

    return response


@router.post("/register")
async def register_endpoint(
    data: RegisterRequestSchema, auth_service: AuthService = Depends(get_auth_service)
) -> RegisterResponseSchema:
    try:
        response = await auth_service.register(data=data)
        return response
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(e)}
        )


@router.post("/refresh-token")
async def refresh_token_endpoint(
    data: RefreshTokenRequestSchema, auth_service: AuthService = Depends(get_auth_service)
) -> RefreshTokenResponse:
    response = await auth_service.refresh_tokens(data=data)

    if response is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid refresh token"},
        )

    return response
