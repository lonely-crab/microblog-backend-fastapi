"""
Сервис для работы с лайками.
"""

from sqlalchemy import Column, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Like

logger = get_logger("like_service")


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
    logger.info(f"User {user_id} is liking tweet {tweet_id}")

    result = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )

    if result.scalar_one_or_none():
        logger.debug(f"User {user_id} already liked tweet {tweet_id}")
        return True

    like = Like(user_id=user_id, tweet_id=tweet_id)

    try:
        session.add(like)
        await session.commit()
        logger.info(f"User {user_id} liked tweet {tweet_id}")

        return True
    except Exception as e:
        logger.exception(f"Failed to add like: {e}")

        return False


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
    logger.info(f"User {user_id} is unliking tweet {tweet_id}")

    await session.execute(
        delete(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    )

    try:
        await session.execute(
            delete(Like).where(
                Like.tweet_id == tweet_id, Like.user_id == user_id
            )
        )
        await session.commit()
        logger.info(f"User {user_id} removed like from tweet {tweet_id}")

        return True
    except Exception as e:
        logger.exception(f"Failed to remove like: {e}")

        return False
