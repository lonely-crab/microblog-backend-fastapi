from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, Column
from datetime import datetime

from dotenv import load_dotenv
from os import getenv
from typing import AsyncGenerator

# load environment variables
load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in .env file.")

engine = create_async_engine(url=DATABASE_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


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
