import logging
import sys
from os import getenv

from dotenv import load_dotenv

load_dotenv()


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _is_debug_mode() -> bool:
    """
    Проверяет, включен ли режим отладки.

    Returns:
        True, если DEBUG=1 в .env или переменных окружения
    """
    return bool(int(getenv("DEBUG", "0")))


def setup_logging() -> None:
    """
    Настраивает базовое логирование для всего приложения.

    Вызывается один раз при старте приложения.
    """
    log_level = "DEBUG" if _is_debug_mode() else "INFO"

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер с префиксом 'microblog.{name}'.

    Args:
        name: Имя модуля (например, 'tweet_service')

    Returns:
        Настраиваемый логгер
    """
    return logging.getLogger(f"microblog.{name}")


logger = logging.getLogger("microblog")
