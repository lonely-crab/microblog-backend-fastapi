"""
Схемы, связанные с лайками.
"""

from .base import BaseSchema
from .user import UserShort


class LikeOut(UserShort):
    """
    Информация о пользователе, поставившем лайк.

    Наследуется от UserShort — содержит id и имя.
    """

    pass


class LikeRequest(BaseSchema):
    """
    Пустая схема-заглушка для запросов на лайк.

    Используется как тело POST-запроса (хотя тела нет).
    """

    pass
