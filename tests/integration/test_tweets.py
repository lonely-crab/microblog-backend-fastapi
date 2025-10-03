import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Tweet, User
from app.schemas import CreateTweetRequest
from app.services.follower_service import follow_user
from app.services.like_service import add_like
from app.services.tweet_service import create_tweet


@pytest.mark.anyio
async def test_create_tweet(client: AsyncClient, test_user_1: User, caplog):
    with caplog.at_level("INFO"):
        response = await client.post(
            "/api/tweets",
            json={"tweet_data": "Test string.", "tweet_media_ids": []},
            headers={"api-key": str(test_user_1.api_key)},
        )
        assert "Tweet created:" in caplog.text
        assert f"{test_user_1.id}" in caplog.text

    assert response.status_code == 200

    data = response.json()
    assert data.get("result") is True
    assert "tweet_id" in data.get("data")


@pytest.mark.anyio
async def test_create_tweet_with_invalid_data(
    client: AsyncClient, test_user_1: User
):
    response = await client.post(
        "/api/tweets",
        json={"tweet_data": "", "tweet_media_ids": []},
        headers={"api-key": str(test_user_1.api_key)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is False
    assert data["error_type"] == "TweetError"
    assert data["error_message"] == "Tweet text cannot be empty."


@pytest.mark.anyio
async def test_delete_own_tweet(
    caplog, client: AsyncClient, test_user_1: User
):
    create_resp = await client.post(
        "/api/tweets",
        json={"tweet_data": "To be deleted", "tweet_media_ids": []},
        headers={"api-key": str(test_user_1.api_key)},
    )
    tweet_id = create_resp.json()["data"]["tweet_id"]

    with caplog.at_level("INFO"):
        delete_resp = await client.delete(
            f"/api/tweets/{tweet_id}",
            headers={"api-key": str(test_user_1.api_key)},
        )
        assert (
            f"Tweet {tweet_id} deleted by user {test_user_1.id}" in caplog.text
        )
        assert delete_resp.json()["result"] is True

    assert delete_resp.status_code == 200


@pytest.mark.anyio
async def test_delete_tweet_exception(
    caplog, mocker, client: AsyncClient, test_user_1: User
):
    mocker.patch("app.api.v1.tweets.delete_tweet", return_value=False)

    with caplog.at_level("WARNING"):
        response = await client.delete(
            "/api/tweets/9999",
            headers={"api-key": str(test_user_1.api_key)},
        )
        assert (
            f"User {test_user_1.id} tried to delete non-existent \
                  or unauthorized tweet 9999\n"
            in caplog.text
        )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is False
    assert data["error_type"] == "NotFound"
    assert data["error_message"] == "Tweet not found or not owned by user"


@pytest.mark.anyio
async def test_delete_other_users_tweet(
    session: AsyncSession,
    client: AsyncClient,
    test_user_1: User,
    test_user_2: User,
):
    # user_1 creates tweet
    await create_tweet(
        session=session,
        request=CreateTweetRequest(tweet_data="Protected", tweet_media_ids=[]),
        author_id=test_user_1.id,
    )
    result = await session.execute(
        select(Tweet.id).where(Tweet.author_id == test_user_1.id)
    )
    tweet_id = result.scalar()

    # user_1 tries to delete it
    resp = await client.delete(
        f"/api/tweets/{tweet_id}",
        headers={"api-key": str(test_user_2.api_key)},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] is False


@pytest.mark.anyio
async def test_get_feed_empty(client: AsyncClient, test_user_1: User):
    resp = await client.get(
        "/api/tweets", headers={"api-key": str(test_user_1.api_key)}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] is True
    assert len(data["data"]["tweets"]) == 0


@pytest.mark.anyio
async def test_get_feed_sorted_by_popularity(
    session: AsyncSession,
    client: AsyncClient,
    test_user_1: User,
    test_user_2: User,
    caplog,
):

    # subscribe user_1 on user_2
    await follow_user(
        session, follower_id=test_user_1.id, following_id=test_user_2.id
    )

    # 2 tweets by user_2
    tweet_1 = await create_tweet(
        session,
        CreateTweetRequest(tweet_data="Popular", tweet_media_ids=[]),
        test_user_2.id,
    )
    tweet_2 = await create_tweet(
        session,
        CreateTweetRequest(tweet_data="Less popular", tweet_media_ids=[]),
        test_user_2.id,
    )

    # add a like on tweet_1
    if tweet_1 is not None:
        await add_like(session, tweet_id=tweet_1, user_id=test_user_1.id)

    # get_feed for user_1
    with caplog.at_level("DEBUG"):
        response = await client.get(
            "/api/tweets", headers={"api-key": str(test_user_1.api_key)}
        )
        assert response.status_code == 200
        assert response.json()["result"] is True
        tweets = response.json()["data"]["tweets"]

        # Check order
        assert tweets[0]["id"] == tweet_1
        assert tweets[1]["id"] == tweet_2

        assert "Feed loaded:" in caplog.text
        assert f"{test_user_1.id}" in caplog.text


@pytest.mark.anyio
async def test_get_tweets_exception(
    caplog, mocker, client: AsyncClient, test_user_1: User
):
    mocker.patch(
        "app.api.v1.tweets.get_user_feed",
        side_effect=Exception("Error while loading feed"),
    )

    with caplog.at_level("ERROR"):
        response = await client.get(
            "/api/tweets", headers={"api-key": str(test_user_1.api_key)}
        )

        assert f"Error loading feed for user {test_user_1.id}" in caplog.text

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is False
