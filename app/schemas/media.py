"""
Схема для медиафайлов.
"""

from .base import BaseSchema


class MediaOut(BaseSchema):
    """
    Ответ с информацией о загруженном медиафайле.

    Attributes:
        id: Уникальный идентификатор медиа
        link: Относительный URL к файлу (например, `/media/abc.jpg`)
    """

    id: int
    link: str
