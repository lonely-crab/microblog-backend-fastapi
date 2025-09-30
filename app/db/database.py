"""
Конфигурация базы данных: движок, сессия, базовый класс моделей.
"""

from datetime import datetime
from os import getenv
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.logging import get_logger

logger = get_logger("database")
load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")

if DATABASE_URL is None and getenv("TESTING") != "1":
    logger.critical("DATABASE_URL is not set in .env file.")
    raise ValueError("DATABASE_URL is not set in .env file.")

no_pw_url = DATABASE_URL
if no_pw_url and "@" in no_pw_url:
    no_pw_url = "postgresql+asyncpg://user:***@" + no_pw_url.split("@")[1]

logger.info(f"Initializing database connection to: {no_pw_url}")


engine = create_async_engine(url=DATABASE_URL)  # type: ignore

async_session_maker = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Генератор сессии для использования в FastAPI (Depends).

    Контекстный менеджер автоматически закрывает сессию.

    Yields:
        Асинхронная сессия SQLAlchemy

    Example:
        >>> async def my_func(db: AsyncSession = Depends(get_db_session)):
        >>>     ...
    """
    async with async_session_maker() as session:
        logger.debug("DB session opened")
        yield session
        logger.debug("DB session closed")


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""

    pass


class TimestampMixin:
    """
    Миксин для добавления поля created_at к нужным моделям.
    """

    created_at = Column(DateTime, default=datetime.now(), nullable=False)
