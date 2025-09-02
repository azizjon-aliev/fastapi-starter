from datetime import timedelta, datetime

from jose import jwt, JWTError
from loguru import logger
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityService:
    """Service for handling security-related operations like token creation and password hashing."""

    def _create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create an access token with a short expiration time."""
        logger.info(f"Creating access token for {data}")

        if expires_delta is None:
            logger.debug("Setting default access token expiration")
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

        return self.__create_token(data, expires_delta)

    def _create_refresh_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a refresh token with a longer expiration time."""
        logger.info(f"create refresh token with data: {data}")

        if expires_delta is None:
            logger.debug("Setting default refresh token expiration")
            expires_delta = timedelta(days=settings.refresh_token_expire_days)

        return self.__create_token(data, expires_delta)

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        logger.info("Verifying password")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def verify_token(token: str) -> str | None:
        """Verify a token and return the username if valid."""
        logger.info(f"Verifying token: {token}")

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Username not found in token payload")
                return None

            logger.info(f"Username found in token payload: {username}")
            return username

        except JWTError as e:
            logger.error(e)
            return None

    @staticmethod
    def _get_password_hash(password: str) -> str:
        """Hash a plain password."""
        logger.info("Hashing password")
        return pwd_context.hash(password)

    @staticmethod
    def __create_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a JWT token with an expiration time."""
        logger.info(f"Creating JWT token: {data}")
        to_encode = data.copy()

        if expires_delta:
            logger.debug(f"Expiring token: {expires_delta}")
            expire = datetime.now() + expires_delta
        else:
            logger.debug("No expiration time")
            expire = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})

        logger.debug(f"to_encode: {to_encode}")
        return jwt.encode(
            claims=to_encode,
            key=settings.secret_key,
            algorithm=settings.algorithm,
        )
