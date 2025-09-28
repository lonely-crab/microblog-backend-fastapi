"""
Сервис для сохранения информации о медиафайлах в БД.
"""

from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Media


async def upload_media(
    session: AsyncSession, file_path: str
) -> int | Column[int]:
    """
    Сохраняет путь к файлу в базе данных.

    Args:
        session: Асинхронная сессия БД
        file_path: Путь к файлу (например, `/media/abc.jpg`)

    Returns:
        ID созданной записи в таблице media

    Example:
        >>> media_id = await upload_media(session, "/media/photo.jpg")
        >>> print(media_id)
        3
    """
    media = Media(file_path=file_path)

    session.add(media)
    await session.flush()
    await session.commit()

    return media.id
