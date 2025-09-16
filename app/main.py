import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1 import tweets, media, users
from app.db.database import engine
from app.db import models

app = FastAPI(
    title="Microblog API",
    description="Backend for a corporate microblogging service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Adding routes
app.include_router(tweets.router)
app.include_router(media.router)
app.include_router(users.router)


# adding tables on startup
@app.on_event("startup")
async def startup_event():
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
        raise Exception(f"Unable to connect to db after {max_retries} attempts.")
    
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

