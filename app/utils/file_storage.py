"""
Утилиты для сохранения загружаемых файлов.
"""

import os
import uuid
from typing import Optional

from fastapi import UploadFile

from app.core.logging import get_logger

logger = get_logger("file_storage")


async def save_upload_file(
    upload_file: UploadFile, dest_folder: str
) -> Optional[str]:
    """
    Сохраняет загруженный файл на диск и возвращает относительный путь.

    Генерирует уникальное имя файла, чтобы избежать коллизий.

    Args:
        upload_file: Загруженный файл
        dest_folder: Папка для сохранения (например, "app/media")

    Returns:
        Относительный URL к файлу (например, `/media/abc.jpg`)

    Raises:
        ValueError: Если расширение файла недопустимо

    Example:
        >>> path = await save_upload_file(file, "app/media")
        >>> print(path)
        /media/abc.jpg
    """
    original_filename = (
        upload_file.filename if upload_file.filename else "unknown"
    )
    logger.info(f"Starting upload of file: {original_filename}")

    ext = (
        os.path.splitext(upload_file.filename)[1]
        if upload_file.filename
        else ".bin"
    )

    acceptable_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".mp4",
        ".mov",
        ".bin",
    ]

    if ext not in acceptable_extensions:
        logger.warning(
            f"Rejected file with unsupported extension: {ext} \
            (file: {original_filename})"
        )
        raise ValueError("Unacceptable file format.")

    os.makedirs(dest_folder, exist_ok=True)
    logger.debug(f"Ensured directory exists: {dest_folder}")

    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(dest_folder, file_name)

    try:
        content = await upload_file.read()
        logger.debug(f"Read {len(content)} bytes from upload")

        with open(file_path, "wb") as f:
            f.write(content)

        relative_url = f"/media/{file_name}"
        logger.info(
            f"File saved successfully: {original_filename} -> {relative_url}"
        )
        return relative_url

    except Exception as e:
        logger.exception(
            f"Failed to save uploaded file: {original_filename} \
                          : {e}"
        )
        raise
