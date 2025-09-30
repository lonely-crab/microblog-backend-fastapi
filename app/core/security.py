"""
Модуль аутентификации через API-ключ.
"""

from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import User

from .logging import get_logger

logger = get_logger("security")


async def get_current_user(
    api_key: str = Header(...), session: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Получает текущего пользователя по API-ключу.

    Функция используется как зависимость во всех защищённых роутах.

    Args:
        api_key: API-ключ из заголовка запроса
        session: Асинхронная сессия БД

    Returns:
        Объект пользователя, если ключ валиден

    Raises:
        HTTPException(403): Если ключ недействителен

    Example:
        >>> @router.get("/users/me")
        >>> async def me(user: User = Depends(get_current_user)):
        >>>     return user
    """
    logger.debug(f"Authenticating user with api-key: {api_key[:1]}...")
    result = await session.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(
            f"Authentication failed: invalid api-key '{api_key[:1]}...'"
        )
        raise HTTPException(status_code=403, detail="Invalid API key")

    logger.info(f"Authenticated user: {user.name} (ID: {user.id})")

    return user
