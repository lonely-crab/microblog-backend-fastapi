import logging
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Media
from app.services.media_service import upload_media


@pytest.mark.anyio
async def test_upload_media(session: AsyncSession):
    file_path = "/media/test.jpg"
    media_id = await upload_media(session=session, file_path=file_path)

    assert media_id is not None

    media = await session.get(Media, media_id)

    assert media is not None
    assert media.file_path == file_path
    assert media.tweet_id is None


@pytest.mark.anyio
async def test_upload_media_exception(caplog):
    # Создаём мок-сессию
    mock_session = AsyncMock()

    # Имитируем выброс исключения при commit()
    mock_session.commit.side_effect = SQLAlchemyError("DB commit failed")

    with pytest.raises(SQLAlchemyError):
        with caplog.at_level(logging.ERROR):
            result = await upload_media(
                session=mock_session, file_path="/media/test.jpg"
            )
            assert result is None
            assert "Failed to upload media" in caplog.text
            assert "DB commit failed" in caplog.text
