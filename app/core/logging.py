import sys
import contextvars
from loguru import logger

from app.core.config import settings

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def request_id_filter(record):
    record["extra"]["request_id"] = request_id_var.get()
    return True


def setup_logging():
    logger.remove()

    common_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{extra[request_id]} | "
        "{level: <8} | "
        "{file}:{function}:{line} | "
        "{message}"
    )

    logger.add(
        sys.stderr,
        format=common_format,
        filter=request_id_filter,
        level=settings.log_level,
        colorize=True,
    )

    logger.add(
        settings.log_file_path,
        format=common_format,
        filter=request_id_filter,
        level=settings.log_file_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression=settings.log_compression,
        serialize=settings.log_serialize,
    )
