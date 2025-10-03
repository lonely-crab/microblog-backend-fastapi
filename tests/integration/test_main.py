import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.models import Tweet, User
from app.main import startup_event
from app.schemas import CreateTweetRequest


@pytest.mark.anyio
async def test_startup_event(mocker, caplog):
    mocker.patch(
        "app.main.engine",
        return_value=create_async_engine(
            url="sqlite+aiosqlite:///:memory:", echo=False
        ),
    )
    with caplog.at_level("INFO"):
        await startup_event()
        assert "Starting up application..." in caplog.text
        assert "Database connection established." in caplog.text
