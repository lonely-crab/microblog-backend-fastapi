"""
Сервис для получения информации о пользователях.
"""

from typing import Optional

from sqlalchemy import Column, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Follower, User


async def get_user_profile(
    session: AsyncSession, target_user_id: Column[int] | int
) -> Optional[dict]:
    """
    Получает профиль пользователя по его ID.

    Включает списки подписчиков и подписок.

    Args:
        session: Асинхронная сессия БД
        target_user_id: ID запрашиваемого пользователя

    Returns:
        Словарь с данными профиля или None, если пользователь не найден

    Example:
        >>> profile = await get_user_profile(session, 1)
        >>> print(profile["name"])
        "Alice"
    """
    result = await session.execute(
        select(User)
        .options(
            selectinload(User.followers).selectinload(
                Follower.follower  # type: ignore
            ),
            selectinload(User.following).selectinload(
                Follower.following  # type: ignore
            ),
        )
        .where(User.id == target_user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    return {
        "id": user.id,
        "name": user.name,
        "followers": [
            {"id": follow.follower.id, "name": follow.follower.name}
            for follow in user.followers
        ],
        "following": [
            {"id": follow.following.id, "name": follow.following.name}
            for follow in user.following
        ],
    }
