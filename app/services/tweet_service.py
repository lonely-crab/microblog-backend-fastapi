"""
Сервис для работы с твитами: создание, удаление, получение ленты.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import Column, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Follower, Like, Media, Tweet
from app.schemas import CreateTweetRequest


async def create_tweet(
    session: AsyncSession, request: CreateTweetRequest, author_id: Column[int]
) -> Optional[Column[int]]:
    """
    Создаёт новый твит с текстом и прикреплёнными медиа.

    Args:
        session: Асинхронная сессия БД
        request: Данные твита (текст и ID медиа)
        author_id: ID автора твита

    Returns:
        ID созданного твита

    Raises:
        ValueError: Если текст твита пустой

    Example:
        >>> tweet_id = await create_tweet(session, request, 1)
        >>> print(tweet_id)
        7
    """
    media_objs = None

    if request.tweet_media_ids:
        media_objects = await session.execute(
            select(Media).where(Media.id.in_(request.tweet_media_ids))
        )

        media_objs = media_objects.scalars().all()

    if request.tweet_data == "" or request.tweet_data is None:
        raise ValueError("Tweet text cannot be empty.")

    tweet = Tweet(author_id=author_id, content=request.tweet_data)
    session.add(tweet)
    await session.flush()

    if media_objs:
        for media_obj in media_objs:
            media_obj.tweet_id = tweet.id
        session.add_all(media_objs)

    await session.commit()
    return tweet.id


async def delete_tweet(
    session: AsyncSession, tweet_id: int, current_user_id: Column[int]
) -> bool:
    """
    Удаляет твит, если он принадлежит указанному пользователю.

    Args:
        session: Асинхронная сессия БД
        tweet_id: ID удаляемого твита
        current_user_id: ID пользователя (должен быть автором)

    Returns:
        True, если твит был найден и удалён, иначе False

    Example:
        >>> success = await delete_tweet(session, 5, 1)
        >>> print(success)
        True
    """
    result = await session.execute(
        select(Tweet).where(
            Tweet.id == tweet_id, Tweet.author_id == current_user_id
        )
    )

    tweet = result.scalar_one_or_none()

    if tweet is None:
        return False

    await session.delete(tweet)
    await session.commit()

    return True


async def get_user_feed(
    session: AsyncSession, user_id: Column[int]
) -> List[dict]:
    """
    Возвращает ленту твитов для пользователя, отсортированную по популярности.

    Лента включает твиты от пользователей, на которых подписан текущий
    пользователь.

    Args:
        session: Асинхронная сессия БД
        user_id: ID пользователя, для которого формируется лента

    Returns:
        Список твитов в формате, готовом к JSON-сериализации

    Example:
        >>> feed = await get_user_feed(session, 1)
        >>> len(feed)
        3
    """
    # users that are followed by our user
    following_subquery = select(Follower.following_id).where(
        Follower.follower_id == user_id
    )

    # get all tweets + join author, media and likes
    result = await session.execute(
        select(Tweet)
        .outerjoin(Like)
        .options(
            selectinload(Tweet.author),  # type: ignore
            selectinload(Tweet.media),
            selectinload(Tweet.likes).selectinload(Like.user),  # type: ignore
        )
        .where(Tweet.author_id.in_(following_subquery))
        .order_by(func.count(Like.tweet_id).desc())
        .group_by(Tweet.id)
    )

    tweets = result.scalars().all()

    return [format_tweet_for_response(tweet=tweet) for tweet in tweets]


def format_tweet_for_response(tweet: Tweet) -> Dict[str, Any]:
    """
    Преобразует ORM-объект твита в словарь для JSON-ответа.

    Args:
        tweet: Объект Tweet из SQLAlchemy

    Returns:
        Словарь с полями: id, content, attachments, author, likes

    Example:
        >>> data = format_tweet_for_response(tweet)
        >>> print(data["content"])
        "Hello world"
    """
    return {
        "id": tweet.id,
        "content": tweet.content,
        "attachments": [media.file_path for media in tweet.media],
        "author": {
            "id": tweet.author_id,
            "name": tweet.author.name,  # type: ignore
        },
        "likes": [
            {"user_id": like.user.id, "name": like.user.name}
            for like in tweet.likes
        ],
    }
