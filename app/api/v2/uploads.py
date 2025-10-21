from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse

from app.core.errors import DomainError

router = APIRouter(prefix="/files", tags=["v2: files"])
UPLOAD_DIR = Path("./_files")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", summary="Upload a single file.")
async def upload_file(file: Annotated[UploadFile, File(...)]):
    """Upload a file and save it to the server."""
    target = UPLOAD_DIR / file.filename
    with target.open("wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)
    return {"filename": file.filename, "size": target.stat().st_size}


@router.get("/download/{filename}", summary="Download a file.")
def download_file(filename: str) -> FileResponse:
    """Download a file by filename."""
    target = UPLOAD_DIR / filename
    if not target.exists():
        raise DomainError("File not found.", code="file_not_found", status_code=404)
    return FileResponse(target)


@router.get("/list", summary="List uploaded files.")
def list_files():
    files = []
    for file in UPLOAD_DIR.iterdir():
        if file.is_file():
            files.append({"filename": file.name, "size": file.stat().st_size})
    return files


# Note: In production, add proper error handling, security checks, and possibly
# virus scanning for uploaded files.
# Also, consider using cloud storage or a dedicated file server for scalability.
# This is a basic example for demonstration purposes only.
# Ensure the UPLOAD_DIR is secure and not publicly accessible in production.
# Clean up old files periodically in production to avoid storage bloat.
# You might want to limit file types and sizes for uploads in production.
# Always validate and sanitize filenames to prevent directory traversal attacks.
# Use async file operations or background tasks for better performance in production.
# Always validate and sanitize filenames to prevent directory traversal attacks.
# Use async file operations or background tasks for better performance in production.
