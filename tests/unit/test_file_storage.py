import logging
import os
from unittest.mock import AsyncMock

import pytest

from app.utils.file_storage import save_upload_file


@pytest.mark.anyio
async def test_save_upload_file():
    mock_upload_file = AsyncMock()
    mock_upload_file.filename = "test.jpg"
    mock_upload_file.read.return_value = b"file content"

    result = await save_upload_file(
        upload_file=mock_upload_file, dest_folder="tests/temp_media"
    )

    assert result is not None
    assert result.startswith("/media/")
    assert result.endswith(".jpg")

    mock_upload_file.read.assert_called_once()

    saved_file_path = os.path.join(
        "tests", "temp_media", os.path.basename(result)
    )
    with open(saved_file_path, "rb") as f:
        content = f.read()
        assert content == b"file content"

    os.remove(saved_file_path)


@pytest.mark.anyio
async def test_save_upload_file_exception(caplog):
    mock_upload_file = AsyncMock()
    mock_upload_file.filename = "test.jpg"
    mock_upload_file.read.return_value = b"file content"
    mock_upload_file.read.side_effect = Exception("File read error")

    with pytest.raises(OSError):
        with caplog.at_level(logging.ERROR):
            result = await save_upload_file(
                upload_file=mock_upload_file, dest_folder="/invalid/path"
            )

            assert result is None

            mock_upload_file.read.assert_called_once()
            assert "Failed to save uploaded file:" in caplog.text
            assert f"{mock_upload_file.filename}" in caplog.text
            assert "File read error" in caplog.text
