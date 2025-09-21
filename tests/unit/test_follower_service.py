import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Follower, Tweet
from app.services.follower_service import follow_user, unfollow_user


@pytest.mark.anyio
async def test_follow_user_new(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    result = await follow_user(
        session=session, follower_id=test_user_1.id, following_id=test_user_2.id
    )
    assert result is True

    follow = await session.get(
        Follower, {"follower_id": test_user_1.id, "following_id": test_user_2.id}
    )
    assert follow is not None


@pytest.mark.anyio
async def test_follow_user_already_following(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    follow = Follower(follower_id=test_user_1.id, following_id=test_user_2.id)
    session.add(follow)
    await session.commit()

    result = await follow_user(
        session=session, follower_id=test_user_1.id, following_id=test_user_2.id
    )
    assert result is True


@pytest.mark.anyio
async def test_unfollow_user(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    follow = Follower(follower_id=test_user_1.id, following_id=test_user_2.id)
    session.add(follow)
    await session.commit()

    result = await unfollow_user(
        session=session, follower_id=test_user_1.id, following_id=test_user_2.id
    )
    assert result is True

    follow = await session.get(
        Follower, {"follower_id": test_user_1.id, "following_id": test_user_2.id}
    )
    assert follow is None


@pytest.mark.anyio
async def test_unfollow_user_not_following(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    result = await unfollow_user(
        session=session, follower_id=test_user_1.id, following_id=test_user_2.id
    )
    assert result is True
