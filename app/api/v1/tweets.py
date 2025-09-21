from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user
from app.db.database import get_db_session
from app.db.models import User
from app.schemas import ApiResponse, CreateTweetRequest
from app.services.like_service import add_like, remove_like
from app.services.tweet_service import (
    create_tweet,
    delete_tweet,
    get_user_feed,
)

router = APIRouter(prefix="/api", tags=["Tweets"])


@router.post("/tweets", response_model=ApiResponse)
async def post_tweets(
    request: CreateTweetRequest,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    try:
        tweet_id = await create_tweet(
            session=session, request=request, author_id=current_user.id
        )
        return ApiResponse(result=True, data={"tweet_id": tweet_id})
    except Exception as e:
        return ApiResponse(
            result=False, error_type="TweetError", error_message=str(e)
        )


@router.get("/tweets")
async def get_tweets(
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    try:
        tweets = await get_user_feed(session=session, user_id=current_user.id)
        return ApiResponse(result=True, data={"tweets": tweets})
    except Exception as e:
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
    success = await delete_tweet(
        session=session, tweet_id=tweet_id, current_user_id=current_user.id
    )  # error 1

    if not success:
        return ApiResponse(
            result=False,
            error_type="NotFound",
            error_message="Tweet not found or not owned by user",
        )

    return ApiResponse(result=True)


@router.post("/tweets/{tweet_id}/likes", response_model=ApiResponse)
async def post_likes(
    tweet_id: int,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    try:
        await add_like(
            session=session, tweet_id=tweet_id, user_id=current_user.id
        )
        return ApiResponse(result=True)
    except Exception as e:
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
    try:
        await remove_like(
            session=session, tweet_id=tweet_id, user_id=current_user.id
        )
        return ApiResponse(result=True)
    except Exception as e:
        return ApiResponse(
            result=False, error_type="UnlikeError", error_message=str(e)
        )
