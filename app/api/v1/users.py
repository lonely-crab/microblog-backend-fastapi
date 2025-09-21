from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db_session
from app.db.models import User
from app.schemas.response import ApiResponse
from app.services.follower_service import follow_user, unfollow_user
from app.services.user_service import get_user_profile

router = APIRouter(prefix="/api", tags=["Users"])


@router.get("/users/me", response_model=ApiResponse)
async def get_my_user_profile(
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    profile = await get_user_profile(
        session=session, target_user_id=current_user.id
    )

    if profile is None:
        return ApiResponse(
            result=False,
            error_type="UserNotFound",
            error_message="User not found",
        )

    return ApiResponse(result=True, data={"user": profile})


@router.get("/users/{user_id}", response_model=ApiResponse)
async def get_user_profile_by_id(
    user_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    profile = await get_user_profile(session=session, target_user_id=user_id)

    if profile is None:
        return ApiResponse(
            result=False,
            error_type="UserNotFound",
            error_message="User not found",
        )

    return ApiResponse(result=True, data={"user": profile})


@router.post("/users/{user_id}/follow", response_model=ApiResponse)
async def post_follow_user(
    user_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == user_id:
        return ApiResponse(
            result=False,
            error_type="FollowError",
            error_message="Cannot follow yourself",
        )

    try:
        await follow_user(
            session=session, follower_id=current_user.id, following_id=user_id
        )
        return ApiResponse(result=True)

    except Exception as e:
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
    try:
        await unfollow_user(
            session=session, follower_id=current_user.id, following_id=user_id
        )
        return ApiResponse(result=True)

    except Exception as e:
        return ApiResponse(
            result=False, error_type="UnfollowError", error_message=str(e)
        )
