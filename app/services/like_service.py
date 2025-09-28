"""
Сервис для работы с лайками.
"""

from sqlalchemy import Column, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Like


async def add_like(
    session: AsyncSession, tweet_id: Column[int] | int, user_id: Column[int]
) -> bool:
    """
    Ставит лайк на твит.

    Если лайк уже есть — ничего не делает (идемпотентность).

    Args:
        session: Асинхронная сессия БД
        tweet_id: ID твита
        user_id: ID пользователя

    Returns:
        True в случае успеха

    Example:
        >>> await add_like(session, 5, 1)
        True
    """
    result = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )

    if result.scalar_one_or_none():
        return True

    like = Like(user_id=user_id, tweet_id=tweet_id)

    session.add(like)
    await session.commit()

    return True


async def remove_like(
    session: AsyncSession, tweet_id: int, user_id: Column[int]
) -> bool:
    """
    Убирает лайк с твита.

    Если лайка не было — ничего не делает (идемпотентность).

    Args:
        session: Асинхронная сессия БД
        tweet_id: ID твита
        user_id: ID пользователя

    Returns:
        True в случае успеха

    Example:
        >>> await remove_like(session, 5, 1)
        True
    """
    await session.execute(
        delete(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )

    await session.commit()

    return True
