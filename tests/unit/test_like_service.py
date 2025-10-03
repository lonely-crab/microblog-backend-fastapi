import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Like, Tweet, User
from app.services.like_service import add_like, remove_like


@pytest.mark.anyio
async def test_add_like_new(
    session: AsyncSession, test_user_1: User, test_tweet_1: Tweet
):
    result = await add_like(
        session=session, tweet_id=test_tweet_1.id, user_id=test_user_1.id
    )
    assert result is True

    like = await session.get(
        Like, {"user_id": test_user_1.id, "tweet_id": test_tweet_1.id}
    )
    assert like is not None


@pytest.mark.anyio
async def test_add_like_already_exists(
    session: AsyncSession, test_user_1: User, test_tweet_1: Tweet
):
    like = Like(user_id=test_user_1.id, tweet_id=test_tweet_1.id)
    session.add(like)
    await session.commit()

    result = await add_like(
        session=session, user_id=test_user_1.id, tweet_id=test_tweet_1.id
    )
    assert result is True


@pytest.mark.anyio
async def test_add_like_exception(caplog):
    # Создаём мок-сессию
    mock_session = AsyncMock()
    mock_result = MagicMock()

    # Имитируем выброс исключения при commit()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    mock_session.commit.side_effect = SQLAlchemyError("DB commit failed")

    with caplog.at_level(logging.ERROR):
        result = await add_like(session=mock_session, tweet_id=1, user_id=1)
        assert result is False
        assert "Failed to add like" in caplog.text


@pytest.mark.anyio
async def test_remove_like_exists(
    session: AsyncSession, test_user_1: User, test_tweet_1: Tweet
):
    await add_like(
        session=session, tweet_id=test_tweet_1.id, user_id=test_user_1.id
    )

    result = await remove_like(
        session=session, tweet_id=test_tweet_1.id, user_id=test_user_1.id
    )
    assert result is True

    like = await session.get(
        Like, {"user_id": test_user_1.id, "tweet_id": test_tweet_1.id}
    )
    assert like is None


@pytest.mark.anyio
async def test_remove_like_not_exists(
    session: AsyncSession, test_user_1: User, test_tweet_1: Tweet
):
    result = await remove_like(
        session=session, tweet_id=test_tweet_1.id, user_id=test_user_1.id
    )
    assert result is True


@pytest.mark.anyio
async def test_remove_like_exception(caplog):
    # Создаём мок-сессию
    mock_session = AsyncMock()
    mock_result = MagicMock()

    # Имитируем выброс исключения при commit()
    mock_result.scalar_one_or_none.return_value = Like()
    mock_session.execute.return_value = mock_result

    mock_session.commit.side_effect = SQLAlchemyError("DB commit failed")

    with caplog.at_level(logging.ERROR):
        result = await remove_like(session=mock_session, tweet_id=1, user_id=1)
        assert result is False
        assert "Failed to remove like" in caplog.text
