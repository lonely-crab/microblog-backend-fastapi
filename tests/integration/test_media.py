from io import BytesIO

import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from mock import AsyncMock, patch

from app.db.models import User


@pytest.mark.anyio
async def test_upload_media_success(
    client: AsyncClient, test_user_1: User, caplog
):
    file_content = b"fake image content"
    file = BytesIO(file_content)
    file.name = "test.jpg"

    with caplog.at_level("INFO"):
        response = await client.post(
            "/api/medias",
            files={"file": ("test.jpg", file, "image/jpeg")},
            headers={"api-key": str(test_user_1.api_key)},
        )
        assert "Media uploaded successfully:" in caplog.text
        assert f"{test_user_1.id}" in caplog.text

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


@pytest.mark.anyio
async def test_post_medias_exception_empty_media(
    mocker, client, caplog, test_user_1
):
    mocker.patch("app.api.v1.media.save_upload_file", return_value=None)

    test_file = ("test.png", b"fake image content", "image/png")

    with caplog.at_level("ERROR"):
        response = await client.post(
            "/api/medias",
            headers={"api-key": test_user_1.api_key},
            files={"file": test_file},
        )
        assert "Failed to upload media" in caplog.text
        assert "File path is empty after saving the file" in caplog.text

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is False
    assert data["error_type"] == "FileUploadError"
    assert "File path is empty" in data["error_message"]
