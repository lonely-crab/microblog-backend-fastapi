import pytest
from httpx import AsyncClient

from app.db.models import User


@pytest.mark.anyio
async def test_get_my_profile(client: AsyncClient, test_user_1: User):
    response = await client.get(
        "/api/users/me", headers={"api-key": str(test_user_1.api_key)}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    user = data["data"]["user"]
    assert user["id"] == test_user_1.id
    assert user["name"] == test_user_1.name
    assert isinstance(user["followers"], list)
    assert isinstance(user["following"], list)


@pytest.mark.anyio
async def test_get_user_profile(client: AsyncClient, test_user_1: User):
    response = await client.get(
        f"/api/users/{test_user_1.id}",
        headers={"api-key": str(test_user_1.api_key)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    user = data["data"]["user"]
    assert user["id"] == test_user_1.id


@pytest.mark.anyio
async def test_follow_unfollow_user(
    client: AsyncClient, test_user_1: User, test_user_2: User
):
    resp = await client.post(
        f"/api/users/{test_user_1.id}/follow",
        headers={"api-key": str(test_user_2.api_key)},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] is True

    resp = await client.delete(
        f"/api/users/{test_user_1.id}/unfollow",
        headers={"api-key": str(test_user_2.api_key)},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] is True


@pytest.mark.anyio
async def test_like_tweet(client: AsyncClient, test_user_1: User):
    create_resp = await client.post(
        "/api/tweets",
        json={"tweet_data": "Like me!", "tweet_media_ids": []},
        headers={"api-key": str(test_user_1.api_key)},
    )
    tweet_id = create_resp.json()["data"]["tweet_id"]

    like_resp = await client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": str(test_user_1.api_key)},
    )
    assert like_resp.status_code == 200
    assert like_resp.json()["result"] is True

    unlike_resp = await client.delete(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": str(test_user_1.api_key)},
    )
    assert unlike_resp.status_code == 200
    assert unlike_resp.json()["result"] is True
