"""
Точка входа в приложение FastAPI.
"""

import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1 import media, tweets, users
from app.core.logging import logger, setup_logging
from app.db.database import engine

setup_logging()


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


# Serving static files (for demo frontend)
app.mount("/media", StaticFiles(directory="/app/app/media"), name="media")


# adding tables on startup
@app.on_event("startup")
async def startup_event():
    """
    Выполняется при старте приложения.

    - Ждёт готовности PostgreSQL

    Raises:
        Exception: Если не удалось подключиться к БД за 15 попыток
    """

    logger.info("Starting up application...")
    max_retries = 15
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established.")
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            await asyncio.sleep(2)
    else:
        logger.critical(
            f"Failed to connect to database after {max_retries} retries."
        )
        raise Exception(
            f"Unable to connect to db after {max_retries} attempts."
        )
