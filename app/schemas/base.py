"""
Базовые Pydantic-схемы.
"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Базовая схема для всех моделей.

    Устанавливает режим `from_attributes=True`, чтобы можно было использовать
    ORM-объекты напрямую.
    """

    model_config = ConfigDict(from_attributes=True)
