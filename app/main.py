"""
Точка входа в приложение FastAPI.
"""

import asyncio

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1 import media, tweets, users
from app.db.database import engine

app = FastAPI(
    title="Microblog API",
    description="Backend for a corporate microblogging service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Adding routes
app.include_router(tweets.router)
app.include_router(media.router)
app.include_router(users.router)


# adding tables on startup
@app.on_event("startup")
async def startup_event():
    """
    Выполняется при старте приложения.

    - Ждёт готовности PostgreSQL

    Raises:
        Exception: Если не удалось подключиться к БД за 15 попыток
    """
    max_retries = 15
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database is ready.")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            await asyncio.sleep(2)
    else:
        raise Exception(
            f"Unable to connect to db after {max_retries} attempts."
        )
