from loguru import logger

from app.core.config import settings


async def cache_factory():
    """Factory function to create and return a RedisCache instance."""
    from aiocache import RedisCache

    logger.info("Creating RedisCache instance")
    return RedisCache(
        endpoint=settings.cache_host,
        port=settings.cache_port,
        db=settings.cache_db,
    )
