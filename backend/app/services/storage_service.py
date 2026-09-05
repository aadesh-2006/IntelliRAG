import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings

class StorageService:
    def __init__(self, base_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadFile) -> tuple[str, str, int]:
        original_filename = file.filename or "untitled"
        suffix = Path(original_filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{suffix}"
        file_path = self.base_dir / unique_filename

        file_size = 0
        file.file.seek(0)
        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    if file_path.exists():
                        file_path.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB}MB."
                    )
                buffer.write(chunk)

        return unique_filename, str(file_path), file_size

    def get_file_path(self, storage_path: str) -> Path:
        path = Path(storage_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on storage."
            )
        return path

    def delete_file(self, storage_path: str) -> bool:
        path = Path(storage_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False

storage_service = StorageService()