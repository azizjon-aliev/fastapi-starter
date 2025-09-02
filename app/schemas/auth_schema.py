from uuid import UUID

from pydantic import BaseModel, model_validator, constr

from app.core.config import settings


class UserResponseSchema(BaseModel):
    id: UUID
    full_name: str
    username: str


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(RefreshTokenRequestSchema):
    access_token: str


class LoginRequestSchema(BaseModel):
    username: constr(
        min_length=3,
        max_length=50,
    )
    password: constr(
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    )


class LoginResponseSchema(TokenResponseSchema): ...


class RegisterRequestSchema(LoginRequestSchema):
    full_name: constr(
        min_length=3,
        max_length=200,
    )
    password_confirm: constr(
        min_length=settings.password_min_length,
        max_length=settings.password_max_length,
    )

    @model_validator(mode="after")
    def check_password_match(self):
        """Ensure that password and password_confirm match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

        return self


class RegisterResponseSchema(LoginResponseSchema): ...


class RefreshTokenResponse(LoginResponseSchema): ...
