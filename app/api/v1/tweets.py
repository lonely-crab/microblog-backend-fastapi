"""
Маршруты для работы с твитами: создание, удаление, лайки, получение ленты.
"""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.core.logging import get_logger
from app.db.database import get_db_session
from app.db.models import User
from app.schemas import ApiResponse, CreateTweetRequest
from app.services.like_service import add_like, remove_like
from app.services.tweet_service import (
    create_tweet,
    delete_tweet,
    get_user_feed,
)

logger = get_logger("tweets_api")

router = APIRouter(prefix="/api", tags=["Tweets"])


@router.post("/tweets", response_model=ApiResponse)
async def post_tweets(
    request: CreateTweetRequest,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Создаёт новый твит от имени авторизованного пользователя.

    Args:
        request: Данные твита (текст и ID медиа)
        api_key: API-ключ пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с tweet_id в случае успеха

    Example:
        >>> POST /api/tweets
        >>> {"tweet_data": "Hello", "tweet_media_ids": [1]}
        >>> Response: {"result": true, "data": {"tweet_id": 10}}

    Raises:
        Exception: При ошибках бизнес-логики или БД
    """
    logger.info(
        f"POST /tweets from user {current_user.id}, \
        text='{request.tweet_data[:30]}...'"
    )

    try:
        tweet_id = await create_tweet(
            session=session, request=request, author_id=current_user.id
        )
        logger.info(f"Tweet created: id={tweet_id}, user={current_user.id}")

        return ApiResponse(result=True, data={"tweet_id": tweet_id})
    except Exception as e:
        logger.exception("Error in post_tweets endpoint")

        return ApiResponse(
            result=False, error_type="TweetError", error_message=str(e)
        )


@router.get("/tweets")
async def get_tweets(
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает ленту твитов от пользователей, на которых подписан текущий
    пользователь.

    Лента отсортирована по популярности (количеству лайков).

    Args:
        api_key: API-ключ пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ со списком твитов

    Example:
        >>> GET /api/tweets
        >>> Response: {"result": true, "data": {"tweets": [...]}}

    Raises:
        Exception: При ошибках получения данных
    """
    logger.info(f" GET /tweets for user {current_user.id}")

    try:
        tweets = await get_user_feed(session=session, user_id=current_user.id)
        logger.debug(
            f"Feed loaded: {len(tweets)} tweets for user {current_user.id}"
        )

        return ApiResponse(result=True, data={"tweets": tweets})
    except Exception as e:
        logger.exception(f"Error loading feed for user {current_user.id}")

        return ApiResponse(
            result=False, error_type="ServerError", error_message=str(e)
        )


@router.delete("/tweets/{tweet_id}", response_model=ApiResponse)
async def delete_tweets(
    tweet_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Удаляет твит, если он принадлежит текущему пользователю.

    Args:
        tweet_id: ID удаляемого твита
        api_key: API-ключ пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с результатом операции

    Example:
        >>> DELETE /api/tweets/5
        >>> Response: {"result": true}

    Raises:
        NotFound: Если твит не найден или не принадлежит пользователю
    """
    logger.info(f"DELETE /tweets/{tweet_id} by user {current_user.id}")

    success = await delete_tweet(
        session=session, tweet_id=tweet_id, current_user_id=current_user.id
    )

    if not success:
        logger.warning(
            f"User {current_user.id} tried to delete non-existent \
            or unauthorized tweet {tweet_id}"
        )

        return ApiResponse(
            result=False,
            error_type="NotFound",
            error_message="Tweet not found or not owned by user",
        )

    logger.info(f"Tweet {tweet_id} deleted by user {current_user.id}")

    return ApiResponse(result=True)


@router.post("/tweets/{tweet_id}/likes", response_model=ApiResponse)
async def post_likes(
    tweet_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Ставит лайк на указанный твит.

    Args:
        tweet_id: ID твита
        api_key: API-ключ пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с результатом операции

    Example:
        >>> POST /api/tweets/5/likes
        >>> Response: {"result": true}
    """
    logger.info(f"POST /tweets/{tweet_id}/likes by user {current_user.id}")
    try:
        await add_like(
            session=session, tweet_id=tweet_id, user_id=current_user.id
        )
        logger.info(f"Like added: tweet={tweet_id}, user={current_user.id}")

        return ApiResponse(result=True)
    except Exception as e:
        logger.exception(f"Failed to add like to tweet {tweet_id}")

        return ApiResponse(
            result=False, error_type="LikeError", error_message=str(e)
        )


@router.delete("/tweets/{tweet_id}/likes", response_model=ApiResponse)
async def delete_likes(
    tweet_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Убирает лайк с указанного твита.

    Args:
        tweet_id: ID твита
        api_key: API-ключ пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с результатом операции

    Example:
        >>> DELETE /api/tweets/5/likes
        >>> Response: {"result": true}
    """
    logger.info(f"DELETE /tweets/{tweet_id}/likes by user {current_user.id}")

    try:
        await remove_like(
            session=session, tweet_id=tweet_id, user_id=current_user.id
        )
        logger.info(f"Like removed: tweet={tweet_id}, user={current_user.id}")

        return ApiResponse(result=True)
    except Exception as e:
        logger.exception(f"Failed to remove like from tweet {tweet_id}")

        return ApiResponse(
            result=False, error_type="UnlikeError", error_message=str(e)
        )
