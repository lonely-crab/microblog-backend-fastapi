from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, func
from sqlalchemy.orm import selectinload

from typing import List, Optional

from app.db.models import Media, Tweet, User, Like, Follower
from app.schemas import CreateTweetRequest


async def create_tweet(session: AsyncSession, request: CreateTweetRequest, author_id: Column[int]) -> Optional[Column[int]]:
    media_objs = None

    if request.tweet_media_ids:
        media_objs = await session.execute(select(Media).where(Media.id.in_(request.tweet_media_ids)))

        media_objs = media_objs.scalars().all()
    
    tweet = Tweet(author_id=author_id, content=request.tweet_data)
    session.add(tweet)
    await session.flush()

    if media_objs:
        for media_obj in media_objs:
            media_obj.tweet_id = tweet.id
        session.add_all(media_objs)
    
    await session.commit()
    return tweet.id


async def delete_tweet(session: AsyncSession, tweet_id: int, current_user_id: int) -> bool:
    result = await session.execute(select(Tweet).where(Tweet.id == tweet_id, Tweet.author_id == current_user_id))

    tweet = result.scalar_one_or_none()

    if tweet is None:
        return False
    
    await session.delete(Tweet)
    await session.commit()

    return True


async def get_user_feed(session: AsyncSession, user_id: int) -> List[dict]:
    # users that are followed by our user
    following_subquery = select(Follower.following_id).where(Follower.follower_id == user_id)

    # get all tweets + join author, media and likes
    result = await session.execute(select(Tweet).options(
        selectinload(Tweet.author),  # should be created in models.py via backref
            selectinload(Tweet.media),
            selectinload(Tweet.likes).selectinload(Like.user)  # should be created in models.py via backref
    )
    .where(Tweet.author_id.in_(following_subquery))
    .order_by(func.count(Like.tweet_id).desc())
    .group_by(Tweet.id)
    )

    tweets = result.scalars().all()
    
    return [format_tweet_for_response(tweet=tweet) for tweet in tweets]

def format_tweet_for_response(tweet: Tweet) -> dict:

    return {
        "id": tweet.id,
        "content": tweet.content,
        "attachments": [media.file_path for media in tweet.media],
        "author": {
            "id": tweet.author_id,
            "name": tweet.author.id # should be created in models.py via backref
        },
        "likes": [
            {"user_id": like.user.id, "name": like.user.name}
            for like in tweet.likes
        ]
    }