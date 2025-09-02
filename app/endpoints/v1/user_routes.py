from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request

from app.db.models.user_model import User
from app.endpoints.dependencies import get_current_user
from app.schemas.auth_schema import (
    UserResponseSchema,
)
from app.utils import rate_limit

router = APIRouter(tags=["User"])


@router.post("/me")
@rate_limit(max_requests=10, time_window=60)
async def me_endpoint(
    request: Request, user: Annotated[User, Depends(get_current_user)]
) -> UserResponseSchema:
    return UserResponseSchema(
        id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
