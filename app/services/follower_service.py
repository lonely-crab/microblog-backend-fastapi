"""
Сервис для работы с подписками между пользователями.
"""

from sqlalchemy import Column, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Follower


async def follow_user(
    session: AsyncSession,
    follower_id: Column[int],
    following_id: Column[int] | int,
) -> bool:
    """
    Подписывает одного пользователя на другого.

    Если подписка уже существует — ничего не делает (идемпотентность).

    Args:
        session: Асинхронная сессия БД
        follower_id: ID пользователя, который подписывается
        following_id: ID пользователя, на которого подписываются

    Returns:
        True в случае успеха

    Example:
        >>> await follow_user(session, 1, 2)
        True
    """
    result = await session.execute(
        select(Follower).where(
            Follower.follower_id == follower_id,
            Follower.following_id == following_id,
        )
    )

    if result.scalar_one_or_none():
        return True

    new_follow = Follower(follower_id=follower_id, following_id=following_id)

    session.add(new_follow)
    await session.commit()

    return True


async def unfollow_user(
    session: AsyncSession,
    follower_id: Column[int],
    following_id: Column[int] | int,
) -> bool:
    """
    Отписывает пользователя от другого.

    Если подписки не было — ничего не делает (идемпотентность).

    Args:
        session: Асинхронная сессия БД
        follower_id: ID пользователя, который отписывается
        following_id: ID пользователя, от которого отписываются

    Returns:
        True в случае успеха

    Example:
        >>> await unfollow_user(session, 1, 2)
        True
    """
    await session.execute(
        delete(Follower).where(
            Follower.follower_id == follower_id,
            Follower.following_id == following_id,
        )
    )

    await session.commit()

    return True
