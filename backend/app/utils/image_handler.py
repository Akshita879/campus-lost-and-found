import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.config import settings


async def save_uploaded_image(file: UploadFile) -> str:
    """
    Validates and saves an uploaded image safely.
    Returns relative file path (e.g. 'uploads/uuid.png').
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing"
        )

    # 1. Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{file_ext}'. Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # 2. Validate MIME type
    if file.content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type '{file.content_type}'. Allowed: {', '.join(settings.ALLOWED_IMAGE_MIME_TYPES)}"
        )

    # 3. Read content and validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB"
        )
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

    # 4. Generate unique server-side filename (prevents collision & traversal attacks)
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    target_path = settings.upload_path / unique_filename

    # Ensure target path does not escape upload directory
    if not target_path.resolve().is_relative_to(settings.upload_path.resolve()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination path"
        )

    with open(target_path, "wb") as f:
        f.write(contents)

    # Return normalized relative path
    return f"{settings.UPLOAD_DIR}/{unique_filename}"


def delete_uploaded_image(relative_path: Optional[str]) -> None:
    """Safely delete an uploaded image file if it exists."""
    if not relative_path:
        return
    try:
        clean_name = Path(relative_path).name
        file_path = settings.upload_path / clean_name
        if file_path.is_file():
            file_path.unlink()
    except Exception:
        pass
