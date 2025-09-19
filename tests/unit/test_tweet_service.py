import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.services.tweet_service import create_tweet, delete_tweet, get_user_feed, format_tweet_for_response
from app.db.models import Tweet, Media, Like, Follower, User


@pytest.mark.anyio
async def test_create_tweet_without_media(session: AsyncSession, test_user_1: User):
    request = type("Request", (), {"tweet_data": "test_string", "tweet_media_ids": []})

    tweet_id = await create_tweet(session=session, request=request, author_id=test_user_1.id)

    assert tweet_id is not None

    tweet = await session.get(Tweet, tweet_id) 
    assert tweet is not None
    assert tweet.content == "test_string"
    assert tweet.author_id == test_user_1.id


@pytest.mark.anyio
async def test_create_tweet_with_media(session: AsyncSession, test_user_1: User, test_media_1: Media):
    request = type("Request", (), {"tweet_data": "test_string", "tweet_media_ids": [test_media_1.id]})

    tweet_id = await create_tweet(session=session, request=request, author_id=test_user_1.id)

    assert tweet_id is not None

    result = await session.execute(select(Tweet).options(selectinload(Tweet.media)).where(Tweet.id == tweet_id))
    tweet = result.scalar_one_or_none()

    assert tweet is not None
    assert len(tweet.media) == 1
    assert tweet.media[0].id == test_media_1.id
    assert tweet.media[0].tweet_id == test_media_1.tweet_id


@pytest.mark.anyio
async def test_delete_tweet_success(session: AsyncSession, test_user_1: User, test_tweet_1: Tweet):

    result = await delete_tweet(session=session, tweet_id=test_tweet_1.id, current_user_id=test_user_1.id)
    assert result is True

    deleted = await session.get(Tweet, test_tweet_1.id)
    assert deleted is None


@pytest.mark.anyio
async def test_delete_tweet_wrong_user(session: AsyncSession, test_user_1: User, test_user_2: User, test_tweet_1: Tweet):
    result = await delete_tweet(session=session, tweet_id=test_tweet_1.id, current_user_id=test_user_2.id)
    assert result is False

    still_exists = await session.get(Tweet, test_tweet_1.id)
    assert still_exists is not None


@pytest.mark.anyio
async def test_get_user_tweet_empty(session: AsyncSession, test_user_1: User):
    tweets = await get_user_feed(session=session, user_id=test_user_1.id)

    assert isinstance(tweets, list)

    assert len(tweets) == 0


@pytest.mark.anyio
async def test_get_user_feed_with_following(session: AsyncSession, test_user_1: User, test_user_2: User, test_tweet_1: Tweet):
    # subscribe user_2 on user_1
    follow = Follower(follower_id=test_user_2.id, following_id=test_user_1.id)
    session.add(follow)
    await session.commit()

    tweets = await get_user_feed(session=session, user_id=test_user_2.id)

    assert isinstance(tweets, list)
    assert tweets[0].get("id") == test_tweet_1.id
    assert len(tweets) == 1
    assert tweets[0].get("author").get("id") == test_user_1.id

