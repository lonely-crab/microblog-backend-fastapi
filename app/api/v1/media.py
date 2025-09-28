"""
Маршруты для загрузки медиафайлов.
"""

from fastapi import APIRouter, Depends, Header, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db_session
from app.db.models import User
from app.schemas.response import ApiResponse
from app.services.media_service import upload_media
from app.utils.file_storage import save_upload_file

router = APIRouter(prefix="/api", tags=["Media"])


@router.post("/medias", response_model=ApiResponse)
async def post_medias(
    file: UploadFile,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Загружает медиафайл на сервер и сохраняет его путь в базе данных.

    Args:
        file: Загружаемый файл (изображение)
        api_key: API-ключ пользователя (в заголовке)
        session: Асинхронная сессия SQLAlchemy
        current_user: Объект текущего пользователя (авторизован)

    Returns:
        JSON-ответ с результатом и media_id в случае успеха

    Example:
        >>> POST /api/medias
        >>> Headers: {"api-key": "test123"}
        >>> Body: form-data with file
        >>> Response: {"result": true, "data": {"media_id": 5}}

    Raises:
        Exception: Если произошла ошибка при сохранении файла
    """
    try:
        file_path = await save_upload_file(
            upload_file=file, dest_folder="app/media"
        )

        media_id = await upload_media(session=session, file_path=file_path)
        return ApiResponse(result=True, data={"media_id": media_id})
    except Exception as e:
        return ApiResponse(
            result=False, error_type="FileUploadError", error_message=str(e)
        )
