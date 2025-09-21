from typing import List

from .base import BaseSchema


class UserShort(BaseSchema):
    id: int
    name: str


class UserProfile(BaseSchema):
    id: int
    name: str
    followers: List[UserShort]
    following: List[UserShort]
