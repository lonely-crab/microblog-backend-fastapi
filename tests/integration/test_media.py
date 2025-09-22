from io import BytesIO

import pytest
from httpx import AsyncClient

from app.db.models import User


@pytest.mark.anyio
async def test_upload_media(client: AsyncClient, test_user_1):
    file_content = b"fake image content"
    file = BytesIO(file_content)
    file.name = "test.jpg"

    response = await client.post(
        "/api/medias",
        files={"file": ("test.jpg", file, "image/jpeg")},
        headers={"api-key": test_user_1.api_key},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "media_id" in data["data"]
    assert isinstance(data["data"]["media_id"], int)


@pytest.mark.anyio
async def test_upload_media_no_file(client: AsyncClient, test_user_1: User):
    response = await client.post(
        "/api/medias", headers={"api-key": str(test_user_1.api_key)}
    )
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.anyio
async def test_upload_media_empty_filename(
    client: AsyncClient, test_user_1: User
):
    file = BytesIO(b"")
    file.name = "empty.jpg"

    response = await client.post(
        "/api/medias",
        files={"file": ("empty.jpg", file, "image/jpeg")},
        headers={"api-key": str(test_user_1.api_key)},
    )
    result = response.json().get("result")
    assert result is True


@pytest.mark.anyio
async def test_upload_media_forbidden_format(
    client: AsyncClient, test_user_1: User
):
    file = BytesIO(b"")
    file.name = "empty.exe"

    response = await client.post(
        "/api/medias",
        files={"file": ("empty.exe", file, "image/jpeg")},
        headers={"api-key": str(test_user_1.api_key)},
    )

    data = response.json()
    result = data.get("result")
    assert result is False

    error_type = data.get("error_type")
    assert error_type == "FileUploadError"

    error_message = data.get("error_message")
    assert error_message == "Unacceptable file format."
