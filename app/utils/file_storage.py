import os
import uuid
from fastapi import UploadFile


async def save_upload_file(upload_file: UploadFile, dest_folder: str) -> str:
    """
    Save file to dest_folder.
    Returns relative path to file (e.g. /media/abc.jpg)
    """

    ext = os.path.splitext(upload_file.filename)[1] if upload_file.filename else ".bin"
    acceptable_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".mp4",
        ".mov",
        ".bin",
    ]

    if ext not in acceptable_extensions:
        raise ValueError("Unacceptable file format.")

    os.makedirs(dest_folder, exist_ok=True)

    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(dest_folder, file_name)

    content = await upload_file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    relative_url = f"/media/{file_name}"
    return relative_url
