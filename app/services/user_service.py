from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models import User, Follower
from typing import Optional


async def get_user_profile(session: AsyncSession, target_user_id: int) -> Optional[dict]:
    result = await session.execute(select(User).options(
        selectinload(User.followers).selectinload(Follower.follower), # should be created in models.py via backref
        selectinload(User.following).selectinload(Follower.following) # should be created in models.py via backref
    ).where(User.id == target_user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None
    
    return {
        "id": user.id,
        "name": user.name,
        "followers": [
            {"id": follow.follower.id, "name": follow.follower.name}
            for follow in user.followers
        ],
        "following": [
            {"id": follow.following.id, "name": follow.following.name}
            for follow in user.following
        ]
    }