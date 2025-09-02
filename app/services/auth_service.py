from loguru import logger

from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    RefreshTokenRequestSchema,
    RefreshTokenResponse,
)
from app.services.security_service import SecurityService


class AuthService(SecurityService):
    """Service for user authentication and registration."""

    def __init__(self, user_repository: UserRepository):
        self._repository = user_repository

    async def register(self, data: RegisterRequestSchema) -> RegisterResponseSchema:
        """Register a new user and return tokens.""" ""
        # Check if user already exists
        existing_user = await self._repository.get_user_by_username(username=data.username)

        if existing_user:
            logger.info(f"User {existing_user.username} already registered.")
            raise ValueError(f"User {data.username} already exists")

        # Hash the password and create the user
        hashed_password = self._get_password_hash(password=data.password)

        # Create user in the repository
        user = await self._repository.create_user(
            full_name=data.full_name,
            username=data.username,
            password=hashed_password,
        )

        logger.debug("Generating new tokens")
        access_token = self._create_access_token(data={"sub": user.username})
        refresh_token = self._create_refresh_token(data={"sub": user.username})

        # Return user data with tokens
        return RegisterResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def login(self, data: LoginRequestSchema) -> LoginResponseSchema | None:
        """Authenticate user and return tokens if successful."""

        # Retrieve user by username
        user = await self._repository.get_user_by_username(username=data.username)

        if not user or not self._verify_password(
            plain_password=data.password,
            hashed_password=user.password,
        ):
            logger.info(f"User {data.username} not found.")
            return None

        logger.debug("Generating new tokens")
        access_token = self._create_access_token(data={"sub": user.username})
        refresh_token = self._create_refresh_token(data={"sub": user.username})

        # Return user data with tokens
        return LoginResponseSchema(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, data: RefreshTokenRequestSchema) -> RefreshTokenResponse | None:
        """Refresh access and refresh tokens."""
        logger.info("Refreshing tokens")
        username = self.verify_token(token=data.refresh_token)

        if not username:
            logger.info("Refreshing tokens failed")
            return None

        logger.debug("Generating new tokens")
        new_access_token = self._create_access_token(data={"sub": username})
        new_refresh_token = self._create_refresh_token(data={"sub": username})

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
