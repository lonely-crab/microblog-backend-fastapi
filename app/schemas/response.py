"""
Схемы ответов API.
"""

from typing import Dict, List

from .base import BaseSchema
from .tweet import TweetOut
from .user import UserProfile


class FeedResponse(BaseSchema):
    """
    Ответ на запрос ленты твитов.

    Attributes:
        result: Успешность операции
        tweets: Список твитов
    """

    result: bool
    tweets: List[TweetOut]


class UserProfileResponse(UserProfile):
    """
    Ответ на запрос профиля пользователя.

    Attributes:
        result: Успешность операции
        user: Данные пользователя (наследуется от UserProfile)
    """

    result: bool
    user: UserProfile


class ApiResponse(BaseSchema):
    """
    Универсальный формат ответа API.

    Все эндпоинты возвращают этот формат.

    Attributes:
        result: true — успех, false — ошибка
        data: Данные ответа (опционально)
        error_type: Тип ошибки (если result == false)
        error_message: Подробное сообщение об ошибке
    """

    result: bool
    data: Dict | None = None
    error_type: str | None = None
    error_message: str | None = None
