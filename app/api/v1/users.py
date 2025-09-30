"""
Маршруты для работы с профилями пользователей и подписками.
"""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import get_current_user
from app.db.database import get_db_session
from app.db.models import User
from app.schemas.response import ApiResponse
from app.services.follower_service import follow_user, unfollow_user
from app.services.user_service import get_user_profile

logger = get_logger("users_api")

router = APIRouter(prefix="/api", tags=["Users"])


@router.get("/users/me", response_model=ApiResponse)
async def get_my_user_profile(
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает профиль текущего авторизованного пользователя.

    Args:
        api_key: API-ключ пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с данными профиля

    Example:
        >>> GET /api/users/me
        >>> Response: {"result": true, "data": {"user": {...}}}
    """
    logger.info(f"GET /users/me from user {current_user.id}")

    profile = await get_user_profile(
        session=session, target_user_id=current_user.id
    )

    if profile is None:
        logger.warning(f"User {current_user.id} profile not found")

        return ApiResponse(
            result=False,
            error_type="UserNotFound",
            error_message="User not found",
        )

    logger.debug(f"Profile retrieved for user {current_user.id}")

    return ApiResponse(result=True, data={"user": profile})


@router.get("/users/{user_id}", response_model=ApiResponse)
async def get_user_profile_by_id(
    user_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает профиль пользователя по его ID.

    Args:
        user_id: ID запрашиваемого пользователя
        api_key: API-ключ текущего пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с данными профиля

    Example:
        >>> GET /api/users/2
        >>> Response: {"result": true, "data": {"user": {...}}}
    """
    logger.info(f"GET /users/{user_id} by user {current_user.id}")

    profile = await get_user_profile(session=session, target_user_id=user_id)

    if profile is None:
        logger.warning(f"Profile not found for user {user_id}")

        return ApiResponse(
            result=False,
            error_type="UserNotFound",
            error_message="User not found",
        )

    logger.debug(f"Profile retrieved: user_id={user_id}")

    return ApiResponse(result=True, data={"user": profile})


@router.post("/users/{user_id}/follow", response_model=ApiResponse)
async def post_follow_user(
    user_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Подписывает текущего пользователя на другого.

    Args:
        user_id: ID пользователя, на которого подписываются
        api_key: API-ключ текущего пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с результатом операции

    Raises:
        FollowError: Если пользователь пытается подписаться на себя
    """
    logger.info(f"POST /users/{user_id}/follow from user {current_user.id}")

    if int(current_user.id) == user_id:
        logger.warning(f"User {current_user.id} tried to follow themselves")

        return ApiResponse(
            result=False,
            error_type="FollowError",
            error_message="Cannot follow yourself",
        )

    try:
        await follow_user(
            session=session, follower_id=current_user.id, following_id=user_id
        )

        logger.info(f"User {current_user.id} followed user {user_id}")

        return ApiResponse(result=True)

    except Exception as e:
        logger.error(
            f"Failed to follow user {user_id} by {current_user.id}: {str(e)}"
        )

        return ApiResponse(
            result=False, error_type="FollowError", error_message=str(e)
        )


@router.delete("/users/{user_id}/unfollow", response_model=ApiResponse)
async def delete_unfollow_user(
    user_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Отписывает текущего пользователя от другого.

    Args:
        user_id: ID пользователя, от которого отписываются
        api_key: API-ключ текущего пользователя
        session: Асинхронная сессия БД
        current_user: Авторизованный пользователь

    Returns:
        JSON-ответ с результатом операции
    """
    logger.info(f"DELETE /users/{user_id}/follow by user {current_user.id}")

    try:
        await unfollow_user(
            session=session, follower_id=current_user.id, following_id=user_id
        )

        logger.info(f"User {current_user.id} unfollowed user {user_id}")

        return ApiResponse(result=True)

    except Exception as e:
        logger.error(f"Failed to unfollow user {user_id}: {str(e)}")

        return ApiResponse(
            result=False, error_type="UnfollowError", error_message=str(e)
        )
