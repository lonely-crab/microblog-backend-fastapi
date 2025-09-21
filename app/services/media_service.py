from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Media


async def upload_media(session: AsyncSession, file_path: str) -> int | Column[int]:
    media = Media(file_path=file_path)

    session.add(media)
    await session.flush()
    await session.commit()

    return media.id
