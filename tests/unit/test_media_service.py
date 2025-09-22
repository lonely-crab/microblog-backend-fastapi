import pytest
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


# add media test for potentially bad files
# + add function in security.py that avoids bad files like .exe etc.
