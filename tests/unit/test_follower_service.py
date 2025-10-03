import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Follower, User
from app.services.follower_service import follow_user, unfollow_user


@pytest.mark.anyio
async def test_follow_user_new(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    result = await follow_user(
        session=session,
        follower_id=test_user_1.id,
        following_id=test_user_2.id,
    )
    assert result is True

    follow = await session.get(
        Follower,
        {"follower_id": test_user_1.id, "following_id": test_user_2.id},
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
        session=session,
        follower_id=test_user_1.id,
        following_id=test_user_2.id,
    )
    assert result is True


@pytest.mark.anyio
async def test_follow_user_exception(caplog):
    # Создаём мок-сессию
    mock_session = AsyncMock()
    mock_result = MagicMock()

    # Имитируем выброс исключения при commit()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    mock_session.commit.side_effect = SQLAlchemyError("DB commit failed")

    with caplog.at_level(logging.ERROR):
        result = await follow_user(
            session=mock_session, follower_id=5, following_id=6
        )

    # Проверяем результат
    assert result is False

    # Проверяем, что add() был вызван
    mock_session.add.assert_called_once()
    assert isinstance(mock_session.add.call_args[0][0], Follower)

    # Проверяем, что commit() был вызван
    mock_session.commit.assert_awaited()

    # Проверяем логирование
    assert len(caplog.records) >= 1
    log_record = caplog.records[0]
    assert log_record.levelname == "ERROR"
    assert "Failed to create follow relationship" in log_record.message
    assert "DB commit failed" in log_record.message


@pytest.mark.anyio
async def test_unfollow_user(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    follow = Follower(follower_id=test_user_1.id, following_id=test_user_2.id)
    session.add(follow)
    await session.commit()

    result = await unfollow_user(
        session=session,
        follower_id=test_user_1.id,
        following_id=test_user_2.id,
    )
    assert result is True

    follow = await session.get(
        Follower,
        {"follower_id": test_user_1.id, "following_id": test_user_2.id},
    )
    assert follow is None


@pytest.mark.anyio
async def test_unfollow_user_not_following(
    session: AsyncSession, test_user_1: User, test_user_2: User
):
    result = await unfollow_user(
        session=session,
        follower_id=test_user_1.id,
        following_id=test_user_2.id,
    )
    assert result is True


@pytest.mark.anyio
async def test_unfollow_user_exception(caplog):
    # Создаём мок-сессию
    mock_session = AsyncMock()

    mock_session.commit.side_effect = SQLAlchemyError("DB commit failed")

    with caplog.at_level(logging.ERROR):
        result = await unfollow_user(
            session=mock_session, follower_id=5, following_id=6
        )

    print(caplog.text)
    # Проверяем результат
    assert result is False

    # Проверяем, что delete() был вызван
    mock_session.execute.assert_awaited()

    # Проверяем, что commit() был вызван
    mock_session.commit.assert_awaited()

    # Проверяем логирование
    assert len(caplog.records) >= 1
    log_record = caplog.records[0]
    assert log_record.levelname == "ERROR"
    assert "Failed to remove follow relationship" in log_record.message
    assert "DB commit failed" in log_record.message
