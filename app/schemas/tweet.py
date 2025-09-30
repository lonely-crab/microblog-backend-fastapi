"""
Схемы, связанные с твитами.
"""

from typing import List

from .base import BaseSchema
from .like import LikeOut
from .user import UserShort


class CreateTweetRequest(BaseSchema):
    """
    Запрос на создание нового твита.

    Attributes:
        tweet_data: Текст твита
        tweet_media_ids: Список ID медиафайлов (опционально)
    """

    tweet_data: str
    tweet_media_ids: List[int] | None = None


class TweetOut(BaseSchema):
    """
    Ответ с информацией о твите.

    Attributes:
        id: Уникальный идентификатор твита
        content: Текст твита
        attachments: Список ссылок на медиа (`/media/...`)
        author: Автор твита (UserShort)
        likes: Список пользователей, поставивших лайк
    """

    id: int
    content: str
    attachments: List[str]
    author: UserShort
    likes: List[LikeOut]
