import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Follower, Like, Media, Tweet, User


@pytest.mark.anyio
async def test_cascade_delete_user(
    session: AsyncSession,
    test_user_1: User,
    test_tweet: Tweet,
    test_media: Media,
    test_like: Like,
    test_follower: Follower,
):
    await session.delete(test_user_1)
    await session.commit()

    result = await session.execute(
        select(Tweet).where(Tweet.id == test_tweet.id)
    )
    assert result.scalar_one_or_none() is None

    result = await session.execute(
        select(Media).where(Media.id == test_media.id)
    )
    assert result.scalar_one_or_none() is None

    result = await session.execute(
        select(Like).where(Like.tweet_id == test_like.tweet_id)
    )
    assert result.scalar_one_or_none() is None

    result = await session.execute(
        select(Follower).where(
            Follower.follower_id == test_follower.follower_id,
            Follower.following_id == test_follower.following_id,
        )
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.anyio
async def test_cascade_delete_tweet(
    session: AsyncSession,
    test_tweet: Tweet,
    test_media: Media,
    test_like: Like,
):
    await session.delete(test_tweet)
    await session.commit()

    result = await session.execute(
        select(Media).where(Media.id == test_media.id)
    )
    assert result.scalar_one_or_none() is None

    result = await session.execute(
        select(Like).where(Like.tweet_id == test_like.tweet_id)
    )
    assert result.scalar_one_or_none() is None
