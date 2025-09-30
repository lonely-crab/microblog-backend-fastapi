"""
Сервис для сохранения информации о медиафайлах в БД.
"""

from typing import Optional

from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Media

logger = get_logger("media_service")


async def upload_media(
    session: AsyncSession, file_path: str
) -> Optional[int | Column[int]]:
    """
    Сохраняет путь к файлу в базе данных.

    Args:
        session: Асинхронная сессия БД
        file_path: Путь к файлу (например, `/media/abc.jpg`)

    Returns:
        ID созданной записи в таблице media;
        None в случае ошибки

    Example:
        >>> media_id = await upload_media(session, "/media/photo.jpg")
        >>> print(media_id)
        3
    """
    logger.info(f"Uploading media: {file_path}")

    media = Media(file_path=file_path)

    session.add(media)
    await session.flush()

    try:
        await session.commit()
        logger.info(
            f"Media uploaded successfully: id={media.id}, path={file_path}"
        )
        return media.id
    except Exception as e:
        logger.exception(f"Failed to upload media {file_path}: {e}")
        raise
