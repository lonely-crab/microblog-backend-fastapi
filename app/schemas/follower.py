"""
Схемы, связанные с подписками.
"""

from .base import BaseSchema


class FollowRequest(BaseSchema):
    """
    Пустая схема-заглушка для запросов на подписку.

    Используется как тело POST-запроса (хотя тела нет).
    """

    pass
