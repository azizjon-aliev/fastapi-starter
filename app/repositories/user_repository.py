from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_model import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username."""
        logger.debug(f"Fetching user by username: {username}")
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def create_user(self, full_name: str, username: str, password: str) -> User:
        """Create a new user in the database."""
        logger.debug(f"Creating new user: {full_name}, {username}")
        user = User(username=username, full_name=full_name, password=password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
