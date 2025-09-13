from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, select, delete

from app.db.models import Like


async def add_like(session: AsyncSession, tweet_id: int, user_id: int) -> bool:
    result = await session.execute(select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id))

    if result.scalar_one_or_none():
        return True
    
    like = Like(user_id=user_id, tweet_id=tweet_id)

    session.add(like)
    await session.commit()
    
    return True

async def remove_like(session: AsyncSession, tweet_id: int, user_id: int) -> bool:
    result = await session.execute(delete(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id))

    await session.commit()

    return True
