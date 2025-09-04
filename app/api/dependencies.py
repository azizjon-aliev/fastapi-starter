from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.models.user_model import User
from app.db.session import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.security_service import SecurityService

bearer_scheme = HTTPBearer()


# Repositories
async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    """Factory function to get UserRepository with a database session."""
    logger.debug("Getting user repository")
    return UserRepository(session=session)


# Services
async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Factory function to get AuthService with UserRepository."""
    logger.debug("Getting auth service")
    return AuthService(user_repository=user_repository)


async def get_security_service() -> SecurityService:
    """Factory function to get SecurityService."""
    logger.debug("Getting security service")
    return SecurityService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    security_service: SecurityService = Depends(get_security_service),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Dependency to get the current authenticated user."""
    logger.debug("Getting current user")
    username = security_service.verify_token(token=credentials.credentials)

    if username is None:
        logger.info("Refreshing tokens failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await user_repo.get_user_by_username(username=username)

    if user is None:
        logger.info("User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
