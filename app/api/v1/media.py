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
