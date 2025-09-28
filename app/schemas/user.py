"""
Схемы, связанные с пользователями.
"""

from typing import List

from .base import BaseSchema


class UserShort(BaseSchema):
    """
    Краткая информация о пользователе.

    Используется в списках (например, подписчики, авторы).

    Attributes:
        id: Уникальный идентификатор
        name: Имя пользователя
    """

    id: int
    name: str


class UserProfile(BaseSchema):
    """
    Полная информация о профиле пользователя.

    Attributes:
        id: Уникальный идентификатор
        name: Имя пользователя
        followers: Список подписчиков (UserShort)
        following: Список пользователей, на которых подписан
    """

    id: int
    name: str
    followers: List[UserShort]
    following: List[UserShort]
