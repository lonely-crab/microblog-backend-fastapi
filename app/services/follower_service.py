from sqlalchemy import Column, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Follower


async def follow_user(
    session: AsyncSession, follower_id: Column[int], following_id: Column[int]
) -> bool:
    result = await session.execute(
        select(Follower).where(
            Follower.follower_id == follower_id,
            Follower.following_id == following_id,
        )
    )

    if result.scalar_one_or_none():
        return True

    new_follow = Follower(follower_id=follower_id, following_id=following_id)

    session.add(new_follow)
    await session.commit()

    return True


async def unfollow_user(
    session: AsyncSession, follower_id: Column[int], following_id: Column[int]
) -> bool:
    await session.execute(
        delete(Follower).where(
            Follower.follower_id == follower_id,
            Follower.following_id == following_id,
        )
    )

    await session.commit()

    return True
