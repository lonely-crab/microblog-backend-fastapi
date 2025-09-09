from .base import BaseSchema

from typing import List


class UserShort(BaseSchema):
    id: int
    name: str


class UserProfile(BaseSchema):
    id: int
    name: str
    followers: List[UserShort]
    following: List[UserShort]