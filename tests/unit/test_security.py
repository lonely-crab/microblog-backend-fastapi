import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models import User


@pytest.mark.anyio
async def test_get_current_user_valid_key(
    session: AsyncSession, test_user_1: User
):
    user = await get_current_user(api_key="key_1", session=session)

    assert user is not None
    assert user.id == test_user_1.id
    assert user.name == test_user_1.name
    assert user.api_key == test_user_1.api_key


@pytest.mark.anyio
async def test_get_current_user_invalid_key(
    session: AsyncSession, test_user_1: User
):

    with pytest.raises(Exception) as exc_info:
        await get_current_user(api_key="invalid_key", session=session)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Invalid API key"
