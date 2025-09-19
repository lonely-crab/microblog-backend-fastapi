import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.services.user_service import get_user_profile


@pytest.mark.anyio
async def test_get_user_profile_found(session: AsyncSession, test_user_1: User):
    user_profile = await get_user_profile(session=session, target_user_id=test_user_1.id)

    assert user_profile is not None
    assert user_profile.get("id") == test_user_1.id
    assert user_profile.get("name") == test_user_1.name
    assert isinstance(user_profile.get("followers"), list)
    assert isinstance(user_profile.get("following"), list)


@pytest.mark.anyio
async def test_get_user_profile_not_found(session: AsyncSession):
    user_profile = await get_user_profile(session=session, target_user_id=999)

    assert user_profile is None