from typing import Dict, List

from .base import BaseSchema
from .tweet import TweetOut
from .user import UserProfile


class FeedResponse(BaseSchema):
    result: bool
    tweets: List[TweetOut]


class UserProfileResponse(UserProfile):
    result: bool
    user: UserProfile


class ApiResponse(BaseSchema):
    result: bool
    data: Dict | None = None
    error_type: str | None = None
    error_message: str | None = None
