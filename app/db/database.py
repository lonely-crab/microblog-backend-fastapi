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

# load environment variables
load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")

if DATABASE_URL is None and getenv("TESTING") != "1":
    raise ValueError("DATABASE_URL is not set in .env file.")

engine = create_async_engine(url=DATABASE_URL)  # type: ignore

async_session_maker = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


# create async session for FastAPI Depends module
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


# base class for all models
class Base(DeclarativeBase):
    pass


# mixin for timestamps
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
