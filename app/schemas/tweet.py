from typing import List

from .base import BaseSchema
from .like import LikeOut
from .user import UserShort


class CreateTweetRequest(BaseSchema):
    tweet_data: str
    tweet_media_ids: List[int] | None = None


class TweetOut(BaseSchema):
    id: int
    content: str
    attachments: List[str]
    author: UserShort
    likes: List[LikeOut]
